import { supabase } from "../supabaseClient"

async function fetchMetadata(linkTable, idColumn, idValue) {
  const [areaLinks, causeLinks, benLinks] = await Promise.all([
    supabase.from(`${linkTable}_areas`).select("area_id").eq(idColumn, idValue),
    supabase.from(`${linkTable}_causes`).select("cause_id").eq(idColumn, idValue),
    supabase.from(`${linkTable}_beneficiaries`).select("ben_id").eq(idColumn, idValue)
  ])

  const areaIds = areaLinks.data?.map(a => a.area_id) || []
  const causeIds = causeLinks.data?.map(c => c.cause_id) || []
  const benIds = benLinks.data?.map(b => b.ben_id) || []

  const [areas, causes, beneficiaries] = await Promise.all([
    areaIds.length > 0
      ? supabase.from("areas").select("area_name, area_level").in("area_id", areaIds)
      : Promise.resolve({ data: [] }),
    causeIds.length > 0
      ? supabase.from("causes").select("cause_name").in("cause_id", causeIds)
      : Promise.resolve({ data: [] }),
    benIds.length > 0
      ? supabase.from("beneficiaries").select("ben_name").in("ben_id", benIds)
      : Promise.resolve({ data: [] })
  ])

  return {
    areas: areas.data || [],
    causes: causes.data || [],
    beneficiaries: beneficiaries.data || []
  }
}

export async function fetchEnrichedFunder(registeredNum) {
  const { data: funder, error } = await supabase
    .from("funders")
    .select("*")
    .eq("registered_num", registeredNum)
    .single()

  if (error) throw error

  const metadata = await fetchMetadata("funder", "registered_num", registeredNum)

  const { data: grantLinks } = await supabase
    .from("funder_grants")
    .select("grant_id")
    .eq("registered_num", registeredNum)

  const grantIds = grantLinks?.map(g => g.grant_id) || []

  let grants = []
  if (grantIds.length > 0) {
    const { data: grantData } = await supabase
      .from("grants")
      .select("grant_id, grant_title, grant_desc, amount, year")
      .in("grant_id", grantIds)
      .order("year", { ascending: false })

    if (grantData && grantData.length > 0) {
      const mostRecentYear = Math.max(...grantData.map(g => g.year || 0))
      const recentGrants = grantData.filter(g => g.year === mostRecentYear)

      const { data: recipientLinks } = await supabase
        .from("recipient_grants")
        .select("grant_id, recipient_id")
        .in("grant_id", recentGrants.map(g => g.grant_id))

      const recipientIds = [...new Set(recipientLinks?.map(r => r.recipient_id) || [])]
      const recipientMap = new Map()

      if (recipientIds.length > 0) {
        const { data: recipients } = await supabase
          .from("recipients")
          .select("recipient_id, recipient_name")
          .in("recipient_id", recipientIds)

        recipients?.forEach(r => recipientMap.set(r.recipient_id, r.recipient_name))
      }

      grants = recentGrants.map(grant => {
        const recipientLink = recipientLinks?.find(r => r.grant_id === grant.grant_id)
        return {
          ...grant,
          recipient_name: recipientLink ? recipientMap.get(recipientLink.recipient_id) : null
        }
      }).sort((a, b) => {
        const nameA = a.recipient_name || ""
        const nameB = b.recipient_name || ""
        return nameA.localeCompare(nameB)
      })
    }
  }

  return { ...funder, ...metadata, grants }
}

export async function fetchEnrichedRecipient(recipientId) {
  const { data: recipient, error } = await supabase
    .from("recipients")
    .select("*")
    .eq("recipient_id", recipientId)
    .single()

  if (error) throw error

  const metadata = await fetchMetadata("recipient", "recipient_id", recipientId)

  const { data: grantLinks } = await supabase
    .from("recipient_grants")
    .select("grant_id")
    .eq("recipient_id", recipientId)
    .limit(5)

  const grantIds = grantLinks?.map(g => g.grant_id) || []

  let grants = []
  if (grantIds.length > 0) {
    const { data: grantData } = await supabase
      .from("grants")
      .select("grant_title, grant_desc, amount, year")
      .in("grant_id", grantIds)
      .order("year", { ascending: false })
      .limit(5)

    grants = grantData || []
  }

  return { ...recipient, ...metadata, grants }
}
export async function fetchRandomPairs(count = 3) {
  const { data: pairs, error } = await supabase
    .from("evaluation_pairs")
    .select("id, funder_registered_num, recipient_id")

  if (error) throw error

  // Get evaluation counts and weight randomisation 
  const { data: responseCounts } = await supabase
    .from("evaluation_responses")
    .select("pair_id")

  const countMap = new Map()
  responseCounts?.forEach(r => {
    countMap.set(r.pair_id, (countMap.get(r.pair_id) || 0) + 1)
  })

  const maxCount = Math.max(...Array.from(countMap.values()), 0)

  const weightedPairs = pairs.flatMap(pair => {
    const evalCount = countMap.get(pair.id) || 0
    const weight = (maxCount - evalCount) + 1
    return Array(weight).fill(pair)
  })

  const shuffled = [...weightedPairs].sort(() => Math.random() - 0.5)

  const selected = []
  const seenIds = new Set()
  for (const pair of shuffled) {
    if (!seenIds.has(pair.id)) {
      selected.push(pair)
      seenIds.add(pair.id)
      if (selected.length === count) break
    }
  }

  return selected
}

export async function fetchEnrichedPair(pair) {
  const [funder, recipient] = await Promise.all([
    fetchEnrichedFunder(pair.funder_registered_num),
    fetchEnrichedRecipient(pair.recipient_id)
  ])

  return { pairId: pair.id, funder, recipient }
}

export async function submitEvaluation(pairId, rating) {
  const { error } = await supabase
    .from("evaluation_responses")
    .insert({ pair_id: pairId, rating })

  if (error) throw error
}
