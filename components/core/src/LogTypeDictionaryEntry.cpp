#include "LogTypeDictionaryEntry.hpp"

// Project headers
#include "ir/parsing.hpp"
#include "type_utils.hpp"
#include "Utils.hpp"

using std::string;

size_t LogTypeDictionaryEntry::get_var_info(
        size_t var_ix,
        ir::VariablePlaceholder& var_placeholder
) const {
    if (var_ix >= m_var_positions.size()) {
        return SIZE_MAX;
    }

    auto var_position = m_var_positions[var_ix];
    var_placeholder = static_cast<ir::VariablePlaceholder>(m_value[var_position]);

    return m_var_positions[var_ix];
}

size_t LogTypeDictionaryEntry::get_data_size () const {
    // NOTE: sizeof(vector[0]) is executed at compile time so there's no risk of an exception at runtime
    return sizeof(m_id) + m_value.length() + m_var_positions.size() * sizeof(m_var_positions[0]) +
           m_ids_of_segments_containing_entry.size() * sizeof(segment_id_t);
}

void LogTypeDictionaryEntry::add_constant (const string& value_containing_constant, size_t begin_pos, size_t length) {
    m_value.append(value_containing_constant, begin_pos, length);
}

void LogTypeDictionaryEntry::add_dictionary_var () {
    m_var_positions.push_back(m_value.length());
    add_dict_var(m_value);
}

void LogTypeDictionaryEntry::add_int_var () {
    m_var_positions.push_back(m_value.length());
    add_int_var(m_value);
}

void LogTypeDictionaryEntry::add_float_var () {
    m_var_positions.push_back(m_value.length());
    add_float_var(m_value);
}

bool LogTypeDictionaryEntry::parse_next_var (const string& msg, size_t& var_begin_pos, size_t& var_end_pos, string& var) {
    auto last_var_end_pos = var_end_pos;
    if (ir::get_bounds_of_next_var(msg, var_begin_pos, var_end_pos)) {
        // Append to log type: from end of last variable to start of current variable
        add_constant(msg, last_var_end_pos, var_begin_pos - last_var_end_pos);

        var.assign(msg, var_begin_pos, var_end_pos - var_begin_pos);
        return true;
    }
    if (last_var_end_pos < msg.length()) {
        // Append to log type: from end of last variable to end
        add_constant(msg, last_var_end_pos, msg.length() - last_var_end_pos);
    }

    return false;
}

void LogTypeDictionaryEntry::clear () {
    m_value.clear();
    m_var_positions.clear();
}

void LogTypeDictionaryEntry::write_to_file (streaming_compression::Compressor& compressor) const {
    compressor.write_numeric_value(m_id);

    string escaped_value;
    get_value_with_unfounded_variables_escaped(escaped_value);
    compressor.write_numeric_value<uint64_t>(escaped_value.length());
    compressor.write_string(escaped_value);
}

ErrorCode LogTypeDictionaryEntry::try_read_from_file (streaming_compression::Decompressor& decompressor) {
    clear();

    ErrorCode error_code;

    error_code = decompressor.try_read_numeric_value<logtype_dictionary_id_t>(m_id);
    if (ErrorCode_Success != error_code) {
        return error_code;
    }

    uint64_t escaped_value_length;
    error_code = decompressor.try_read_numeric_value(escaped_value_length);
    if (ErrorCode_Success != error_code) {
        return error_code;
    }
    string escaped_value;
    error_code = decompressor.try_read_string(escaped_value_length, escaped_value);
    if (ErrorCode_Success != error_code) {
        return error_code;
    }

    // Decode encoded logtype
    bool is_escaped = false;
    string constant;
    for (size_t i = 0; i < escaped_value_length; ++i) {
        char c = escaped_value[i];

        if (is_escaped) {
            constant += c;
            is_escaped = false;
        } else if (ir::cVariablePlaceholderEscapeCharacter == c) {
            is_escaped = true;
        } else {
            if (enum_to_underlying_type(ir::VariablePlaceholder::Integer) == c) {
                add_constant(constant, 0, constant.length());
                constant.clear();
                add_int_var();
            } else if (enum_to_underlying_type(ir::VariablePlaceholder::Float) == c) {
                add_constant(constant, 0, constant.length());
                constant.clear();
                add_float_var();
            } else if (enum_to_underlying_type(ir::VariablePlaceholder::Dictionary) == c) {
                add_constant(constant, 0, constant.length());
                constant.clear();
                add_dictionary_var();
            }
            else {
                constant += c;
            }
        }
    }
    if (constant.empty() == false) {
        add_constant(constant, 0, constant.length());
    }

    return error_code;
}

void LogTypeDictionaryEntry::read_from_file (streaming_compression::Decompressor& decompressor) {
    auto error_code = try_read_from_file(decompressor);
    if (ErrorCode_Success != error_code) {
        throw OperationFailed(error_code, __FILENAME__, __LINE__);
    }
}

void LogTypeDictionaryEntry::get_value_with_unfounded_variables_escaped (string& escaped_logtype_value) const {
    auto value_view = static_cast<std::string_view>(m_value);
    size_t begin_ix = 0;
    // Reset escaped value and reserve enough space to at least contain the whole value
    escaped_logtype_value.clear();
    escaped_logtype_value.reserve(value_view.length());
    for (auto var_position : m_var_positions) {
        size_t end_ix = var_position;

        ir::escape_and_append_constant_to_logtype(
                value_view.substr(begin_ix, end_ix - begin_ix),
                escaped_logtype_value
        );

        // Add variable placeholder
        escaped_logtype_value += value_view[end_ix];

        // Move begin to start of next portion of logtype between variables
        begin_ix = end_ix + 1;
    }
    // Escape any variable placeholders in remainder of value
    ir::escape_and_append_constant_to_logtype(value_view.substr(begin_ix), escaped_logtype_value);
}
