#include "VariableDictionaryWriter.hpp"

// Project headers
#include "dictionary_utils.hpp"
#include "spdlog_with_specializations.hpp"

bool VariableDictionaryWriter::add_entry (const std::string& value, variable_dictionary_id_t& id) {
    bool new_entry = false;

    const auto ix = m_value_to_id.find(value);
    if (m_value_to_id.end() != ix) {
        id = ix->second;
    } else {
        // Entry doesn't exist so create it

        if (m_next_id > m_max_id) {
            SPDLOG_ERROR("VariableDictionaryWriter ran out of IDs.");
            throw OperationFailed(ErrorCode_OutOfBounds, __FILENAME__, __LINE__);
        }

        // Assign ID
        id = m_next_id;
        ++m_next_id;

        // Insert the ID obtained from the database into the dictionary
        auto entry = VariableDictionaryEntry(value, id);
        m_value_to_id[value] = id;

        new_entry = true;

        // TODO: This doesn't account for the segment index that's constantly updated
        m_data_size += entry.get_data_size();

        entry.write_to_file(m_dictionary_compressor);
    }
    return new_entry;
}
