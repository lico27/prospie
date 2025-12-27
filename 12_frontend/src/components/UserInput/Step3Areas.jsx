import { useState, useEffect } from "react"
import CreatableSelect from "react-select/creatable"
import { supabase } from "../../supabaseClient"

function Step3Areas({ selectedAreas, onChange }) {
  const [areaOptions, setAreaOptions] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchAreas = async () => {
      try {
        const { data, error } = await supabase
          .from("areas")
          .select("area_id, area_name, area_level")
          .order("area_level")
          .order("area_name")

        if (error) throw error

        //group areas by level
        const groupedAreas = data.reduce((acc, area) => {
          const level = area.area_level || "Other"
          if (!acc[level]) {
            acc[level] = []
          }
          acc[level].push({
            value: area.area_name,
            label: area.area_name
          })
          return acc
        }, {})

        const formattedOptions = Object.keys(groupedAreas)
          .sort()
          .map(level => ({
            label: level.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase()),
            options: groupedAreas[level]
          }))

        setAreaOptions(formattedOptions)
      } catch (err) {
        console.error("Error fetching areas:", err)
      } finally {
        setLoading(false)
      }
    }

    fetchAreas()
  }, [])

  const selectedOptions = selectedAreas.map(area => ({
    value: area,
    label: area
  }))

  const handleChange = (selected) => {
    const areaNames = selected ? selected.map(option => option.value) : []
    onChange(areaNames)
  }

  //apply styles
  const customStyles = {
    control: (provided, state) => ({
      ...provided,
      backgroundColor: "rgba(26, 22, 37, 0.6)",
      borderColor: state.isFocused ? "rgba(111, 163, 168, 0.6)" : "rgba(142, 125, 179, 0.3)",
      borderRadius: "8px",
      padding: "0.25rem",
      boxShadow: state.isFocused ? "0 0 0 3px rgba(111, 163, 168, 0.1)" : "none",
      transition: "all 0.3s ease",
      "&:hover": {
        borderColor: "rgba(142, 125, 179, 0.5)"
      }
    }),
    menu: (provided) => ({
      ...provided,
      backgroundColor: "rgba(42, 38, 54, 0.95)",
      border: "1px solid rgba(142, 125, 179, 0.3)",
      borderRadius: "8px",
      backdropFilter: "blur(10px)",
      boxShadow: "0 8px 32px rgba(0, 0, 0, 0.3)"
    }),
    menuList: (provided) => ({
      ...provided,
      padding: "0.5rem",
      maxHeight: "300px",
      "::-webkit-scrollbar": {
        width: "8px"
      },
      "::-webkit-scrollbar-track": {
        background: "rgba(26, 22, 37, 0.6)"
      },
      "::-webkit-scrollbar-thumb": {
        background: "rgba(142, 125, 179, 0.3)",
        borderRadius: "4px"
      },
      "::-webkit-scrollbar-thumb:hover": {
        background: "rgba(142, 125, 179, 0.5)"
      }
    }),
    option: (provided, state) => ({
      ...provided,
      backgroundColor: state.isSelected
        ? "rgba(142, 125, 179, 0.3)"
        : state.isFocused
        ? "rgba(142, 125, 179, 0.15)"
        : "transparent",
      color: state.isSelected ? "#dcd3ed" : "#c9c0de",
      padding: "0.6rem 0.75rem",
      cursor: "pointer",
      borderRadius: "4px",
      fontSize: "0.9rem",
      transition: "all 0.2s ease",
      "&:active": {
        backgroundColor: "rgba(142, 125, 179, 0.25)"
      }
    }),
    multiValue: (provided) => ({
      ...provided,
      backgroundColor: "rgba(142, 125, 179, 0.2)",
      border: "1px solid rgba(142, 125, 179, 0.3)",
      borderRadius: "6px"
    }),
    multiValueLabel: (provided) => ({
      ...provided,
      color: "#dcd3ed",
      fontSize: "0.85rem",
      padding: "0.3rem 0.5rem"
    }),
    multiValueRemove: (provided) => ({
      ...provided,
      color: "#c9c0de",
      ":hover": {
        backgroundColor: "rgba(220, 92, 92, 0.3)",
        color: "#ffb3b3",
        borderRadius: "0 4px 4px 0"
      }
    }),
    placeholder: (provided) => ({
      ...provided,
      color: "rgba(201, 192, 222, 0.4)",
      fontSize: "0.9rem"
    }),
    input: (provided) => ({
      ...provided,
      color: "#ffffff"
    }),
    groupHeading: (provided) => ({
      ...provided,
      backgroundColor: "rgba(111, 163, 168, 0.1)",
      color: "#8ebcc0",
      fontSize: "0.85rem",
      fontWeight: "700",
      textTransform: "uppercase",
      letterSpacing: "0.05em",
      padding: "0.5rem 0.75rem",
      marginBottom: "0.25rem",
      borderRadius: "4px"
    }),
    group: (provided) => ({
      ...provided,
      paddingTop: "0.25rem",
      paddingBottom: "0.5rem"
    }),
    indicatorSeparator: (provided) => ({
      ...provided,
      backgroundColor: "rgba(142, 125, 179, 0.3)"
    }),
    dropdownIndicator: (provided) => ({
      ...provided,
      color: "#c9c0de",
      "&:hover": {
        color: "#dcd3ed"
      }
    }),
    clearIndicator: (provided) => ({
      ...provided,
      color: "#c9c0de",
      "&:hover": {
        color: "#ffb3b3"
      }
    }),
    noOptionsMessage: (provided) => ({
      ...provided,
      color: "#c9c0de",
      fontSize: "0.9rem",
      padding: "0.75rem"
    })
  }

  return (
    <div className="form-group">
      <div className="question-heading">
        <span className="question-heading-text">Where does your project operate?</span>
      </div>
      <p className="form-helper-text">Select all that apply. Type to search or add a custom area.</p>
      {loading ? (
        <div>Loading areas...</div>
      ) : (
        <CreatableSelect
          isMulti
          options={areaOptions}
          value={selectedOptions}
          onChange={handleChange}
          placeholder="Select areas..."
          styles={customStyles}
          className="react-select-container"
          classNamePrefix="react-select"
          formatCreateLabel={(inputValue) => `Add "${inputValue}"`}
        />
      )}
    </div>
  )
}

export default Step3Areas
