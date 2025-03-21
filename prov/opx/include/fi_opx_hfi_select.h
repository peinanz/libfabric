/*
 * Copyright (C) 2021 by Cornelis Networks.
 *
 * This software is available to you under a choice of one of two
 * licenses.  You may choose to be licensed under the terms of the GNU
 * General Public License (GPL) Version 2, available from the file
 * COPYING in the main directory of this source tree, or the
 * BSD license below:
 *
 *     Redistribution and use in source and binary forms, with or
 *     without modification, are permitted provided that the following
 *     conditions are met:
 *
 *      - Redistributions of source code must retain the above
 *        copyright notice, this list of conditions and the following
 *        disclaimer.
 *
 *      - Redistributions in binary form must reproduce the above
 *        copyright notice, this list of conditions and the following
 *        disclaimer in the documentation and/or other materials
 *        provided with the distribution.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 * MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 * NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
 * BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
 * ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
 * CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */
#ifndef _FI_OPX_HFI_SELECT_H_
#define _FI_OPX_HFI_SELECT_H_

enum hfi_selector_type { HFI_SELECTOR_FIXED = 1, HFI_SELECTOR_MAPBY, HFI_SELECTOR_DEFAULT };
enum hfi_selector_mapby_type { HFI_SELECTOR_MAPBY_NUMA = 1, HFI_SELECTOR_MAPBY_CORE };

#define HFI_SELECTOR_SUBSTRING_MAX 4096
#define HFI_SELECTOR_UNIT_MAX	   INT_MAX
#define HFI_SELECTOR_NUMA_MAX	   INT_MAX
#define HFI_SELECTOR_CORE_MAX	   INT_MAX

struct hfi_selector {
	enum hfi_selector_type type;
	int		       unit;
	union {
		struct {
			enum hfi_selector_mapby_type type;
			int			     rangeS;
			int			     rangeE;
		} mapby;
	};
};

/**
 * Parse an hfi_selector element from string starting at @c start.
 *
 * Parse one of two forms:
 * - Fixed: <hfi-unit>
 * - MatchBy: <mapby-resource-type>:<hfi-unit>:<selector-data>
 * Where:
 * 		<hfi-unit> : [0-9]+
 * 		<mapby-resource-type> : 'numa'
 * 		<selector-data> : ???
 *
 * @return On success, @c char* to first character of next element or @c char* to '\0' in @c start if @c '\0' was
 * encountered. @c NULL on error.
 */
const char *hfi_selector_next(const char *start, struct hfi_selector *selector);

#endif /* _FI_OPX_HFI_SELECT_H_ */
