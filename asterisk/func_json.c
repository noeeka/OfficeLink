/*
 * Asterisk -- An open source telephony toolkit.
 *
 * Copyright (c) 2003-2006 systec.  All rights reserved.
 *
 * systec <systec@systechn.com>
 *
 * This code is released by the author with no restrictions on usage.
 *
 * See http://www.asterisk.org for more information about
 * the Asterisk project. Please do not directly contact
 * any of the maintainers of this project for assistance;
 * the project provides a web site, mailing lists and IRC
 * channels for your use.
 *
 */

/*! \file
 * 
 * \brief json function
 *
 * \author systec <systec@systechn.com>
 *
 * \ingroup functions
 */

/*** MODULEINFO
	<depend>jansson</depend>
	<depend>sqlite3</depend>
	<support_level>extended</support_level>
 ***/

#include "asterisk.h"

ASTERISK_FILE_VERSION(__FILE__, "$Revision$")

#include "asterisk/file.h"
#include "asterisk/channel.h"
#include "asterisk/pbx.h"
#include "asterisk/module.h"
#include "asterisk/app.h"

#define AST_MODULE "func_json"

#include <sqlite3.h>
#include <jansson.h>

/*** DOCUMENTATION
	<function name="JSON_OBJECT" language="en_US">
		<synopsis>
			Get item of JSON Object.	
		</synopsis>
		<syntax>
			<parameter name="key" required="true" argsep=":">
				<para>key of item</para>
			</parameter>
		</syntax>
		<description>
			<para>key</para>
		</description>
	</function>
	<function name="JSON_ARRAY" language="en_US">
		<synopsis>
			Get JSON item of JSON array.	
		</synopsis>
		<syntax>
			<parameter name="index" required="true" argsep=":">
				<para>index of item</para>
			</parameter>
		</syntax>
		<description>
			<para>index</para>
		</description>
	</function>
	<function name="JSON_EXTENSION" language="en_US">
		<synopsis>
			Get EXTENSION info as JSON.	
		</synopsis>
		<syntax>
			<parameter name="extension" required="true" argsep=":">
				<para>extension</para>
			</parameter>
		</syntax>
		<description>
			<para>extension</para>
		</description>
	</function>

 ***/

/*
 * Parse text into a JSON object. If text is valid JSON, returns a
 * json_t structure, otherwise prints and error and returns null.
 */
static json_t *load_json(const char *text) {
    json_t *root;
    json_error_t error;

    root = json_loads(text, 0, &error);

    if (root) {
        return root;
    } else {
		ast_log(LOG_ERROR, "json error on line %d: %s %s\n", error.line, error.text, text);
        return (json_t *)0;
    }
}

void print_json_aux(json_t *element, int indent) {
    switch (json_typeof(element)) {
    case JSON_OBJECT:
        print_json_object(element, indent);
        break;
    case JSON_ARRAY:
        print_json_array(element, indent);
        break;
    case JSON_STRING:
        print_json_string(element, indent);
        break;
    case JSON_INTEGER:
        print_json_integer(element, indent);
        break;
    case JSON_REAL:
        print_json_real(element, indent);
        break;
    case JSON_TRUE:
        print_json_true(element, indent);
        break;
    case JSON_FALSE:
        print_json_false(element, indent);
        break;
    case JSON_NULL:
        print_json_null(element, indent);
        break;
    default:
        fprintf(stderr, "unrecognized JSON type %d\n", json_typeof(element));
    }
}

static int acf_json_object_exec(struct ast_channel *chan, const char *cmd, char *data, char *buf, size_t len)
{
	int ret = -1;
    
    AST_DECLARE_APP_ARGS(args,
		AST_APP_ARG(object);
		AST_APP_ARG(key);
	);

	char *parse = ast_strdupa(data);

	AST_STANDARD_APP_ARGS(args, parse);

    json_t *root = load_json(args.object);

    if (root) {
        json_t *item = json_object_get(root, args.key);
        if(item) {
            char *buf_item = json_dumps(item, 0); 
            if(buf_item) {
                int item_len = strlen(buf_item);
                if(item_len > len-1) {
                    item_len = len-1;
                }
                if(item_len > 1) {
                    strncpy(buf, buf_item, item_len);
                }
                free(buf_item);
            }
        }
        json_decref(root);
    }
	return ret;
}

static int acf_json_array_exec(struct ast_channel *chan, const char *cmd, char *data, char *buf, size_t len)
{
	int ret = -1;
	return ret;
}

static int acf_json_extension_exec(struct ast_channel *chan, const char *cmd, char *data, char *buf, size_t len)
{
	int ret = -1;
	return ret;
}

static struct ast_custom_function acf_json_object = {
	.name = "JSON_OBJECT",
	.read = acf_json_object_exec,
};

static struct ast_custom_function acf_json_array = {
	.name = "JSON_ARRAY",
	.read = acf_json_array_exec,
};

static struct ast_custom_function acf_json_extension = {
	.name = "JSON_EXTENSION",
	.read = acf_json_extension_exec,
};

static int unload_module(void)
{
	int res = 0;

    res |= ast_custom_function_unregister(&acf_json_object);
    res |= ast_custom_function_unregister(&acf_json_array);
    res |= ast_custom_function_unregister(&acf_json_extension);

	return res;
}

static int load_module(void)
{
	int res = 0;

   	res |= ast_custom_function_register(&acf_json_object);
	res |= ast_custom_function_register(&acf_json_array);
	res |= ast_custom_function_register(&acf_json_extension);

	return res;
}

AST_MODULE_INFO_STANDARD(ASTERISK_GPL_KEY, "func_json");
