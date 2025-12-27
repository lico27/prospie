let ukcat_data_cache = null

//fetch classifications data
export async function fetchUkcatData() {
  if (ukcat_data_cache) {
    return ukcat_data_cache
  }

  try {
    const response = await fetch("https://raw.githubusercontent.com/lico27/ukcat/main/data/ukcat.csv")
    const csvText = await response.text()

    //parse csv
    const lines = csvText.split("\n")
    const headers = lines[0].split(",").map(h => h.trim().replace(/^"|"$/g, ""))

    const data = []
    for (let i = 1; i < lines.length; i++) {
      if (!lines[i].trim()) continue

      //handle quoted fields
      const values = parseCsvLine(lines[i])
      if (values.length < headers.length) continue

      const row = {}
      headers.forEach((header, index) => {
        row[header] = values[index] || ""
      })
      data.push(row)
    }

    ukcat_data_cache = data
    return data
  } catch (error) {
    console.error("Error fetching UKCAT data:", error)
    return []
  }
}

//parse csv line with quoted fields
function parseCsvLine(line) {
  const result = []
  let current = ""
  let inQuotes = false

  for (let i = 0; i < line.length; i++) {
    const char = line[i]

    if (char === '"') {
      inQuotes = !inQuotes
    } else if (char === "," && !inQuotes) {
      result.push(current.trim().replace(/^"|"$/g, ""))
      current = ""
    } else {
      current += char
    }
  }

  result.push(current.trim().replace(/^"|"$/g, ""))
  return result
}

/**
 *  extract classifications
 *
 * @param {Object} data
 * @param {Array} ukcatData
 * @param {Array} existingKeywords
 * @returns {Array}
 */
export function extractClassifications(data, ukcatData, existingKeywords = []) {
  const matchedItems = new Set(existingKeywords.map(k => k.toLowerCase()))

  //combine all text sections
  const textSections = []
  if (data.activities) textSections.push(data.activities)
  if (data.objectives) textSections.push(data.objectives)
  if (data.areas) {
    const areaNames = Array.isArray(data.areas) ? data.areas : []
    textSections.push(areaNames.join(" "))
  }
  if (data.beneficiaries) {
    const benNames = Array.isArray(data.beneficiaries) ? data.beneficiaries : []
    textSections.push(benNames.join(" "))
  }
  if (data.causes) {
    const causeNames = Array.isArray(data.causes) ? data.causes : []
    textSections.push(causeNames.join(" "))
  }

  const textToSearch = textSections.join(" ").toLowerCase()

  //match against ukcat
  ukcatData.forEach(ukcatRow => {
    const tag = ukcatRow.tag
    const regexPattern = ukcatRow["Regular expression"]
    const excludePattern = ukcatRow["Exclude regular expression"]

    if (!tag || !regexPattern) return

    try {
      //check main pattern
      const mainRegex = new RegExp(regexPattern, "i")
      if (mainRegex.test(textToSearch)) {
        //check exclude pattern
        let shouldExclude = false
        if (excludePattern && excludePattern.trim()) {
          try {
            const excludeRegex = new RegExp(excludePattern, "i")
            shouldExclude = excludeRegex.test(textToSearch)
          } catch (e) {
          }
        }

        if (!shouldExclude) {
          matchedItems.add(tag.toLowerCase())
        }
      }
    } catch (e) {
      console.warn(`Invalid regex for tag ${tag}:`, e)
    }
  })

  //match areas
  if (data.areas && Array.isArray(data.areas)) {
    data.areas.forEach(areaName => {
      if (!areaName) return
      try {
        const pattern = new RegExp(`\\b${escapeRegex(areaName)}\\b`, "i")
        if (pattern.test(textToSearch)) {
          matchedItems.add(areaName.toLowerCase())
        }
      } catch (e) {
        matchedItems.add(areaName.toLowerCase())
      }
    })
  }

  //convert case or capitalise
  const result = Array.from(matchedItems).map(item => {
    const ukcatMatch = ukcatData.find(row => row.tag && row.tag.toLowerCase() === item)
    if (ukcatMatch) return ukcatMatch.tag
    if (data.areas && Array.isArray(data.areas)) {
      const areaMatch = data.areas.find(a => a && a.toLowerCase() === item)
      if (areaMatch) return areaMatch
    }
    return item.charAt(0).toUpperCase() + item.slice(1)
  })

  return result.sort()
}

//escape special regex characters
function escapeRegex(string) {
  return string.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")
}
