/*
 * Copyright(c) 2021 ADLINK Technology Limited and others
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License v. 2.0 which is available at
 * http://www.eclipse.org/legal/epl-2.0, or the Eclipse Distribution License
 * v. 1.0 which is available at
 * http://www.eclipse.org/org/documents/edl-v10.php.
 *
 * SPDX-License-Identifier: EPL-2.0 OR BSD-3-Clause
 */
#include <assert.h>
#include <errno.h>
#include <stdlib.h>
#include <string.h>

#include "types.h"
#include "generator.h"
#include "context.h"

#include "idl/file.h"
#include "idl/retcode.h"
#include "idl/stream.h"
#include "idl/string.h"
#include "idl/version.h"
#include "idl/processor.h"


idl_retcode_t
generate(const idl_pstate_t *pstate)
{
    idl_retcode_t ret = IDL_RETCODE_NO_MEMORY;
    /* 
        The Python backend assumes you will always want to save into the current working directory.
        Any handling for differences will be done by switching that work directory on the python side.
    */

    idlpy_ctx ctx = idlpy_new_ctx("./");

    ret = generate_types(pstate, ctx);
    
    return ret;
}
