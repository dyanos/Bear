%{
#include "y.tab.h"
#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>

int _bDebugFlag = 1;

void dbgmsg_printf(char* format, ...);
%}

%%
use       { dbgmsg_printf("use\n"); return USE; }
import    { dbgmsg_printf("import\n"); return IMPORT; }
def       { dbgmsg_printf("def\n"); return DEF; }
if        { dbgmsg_printf("if\n"); return IF; }
and       { dbgmsg_printf("and\n"); return AND; }
or        { dbgmsg_printf("or\n"); return OR; }
not       { dbgmsg_printf("not\n"); return NOT; }
for       { dbgmsg_printf("for\n"); return FOR; }
match     { dbgmsg_printf("match\n"); return MATCH; }
return    { dbgmsg_printf("return\n"); return RETURN; }
[ \n\t]   { /* skip */ }
"=>"      { dbgmsg_printf("=>\n"); return BIGRIGHTARROW; }
"_"       { dbgmsg_printf("underscore\n"); return '_'; }
"."       { dbgmsg_printf("dot\n"); return '.'; }
","       { dbgmsg_printf("comma\n"); return ','; }
":"       { dbgmsg_printf(":\n"); return ':'; }
";"       { dbgmsg_printf("semicolon\n"); return ';'; }
"["       { dbgmsg_printf("[\n"); return '['; }
"]"       { dbgmsg_printf("]\n"); return ']'; }
"{"       { dbgmsg_printf("{\n"); return '{'; }
"}"       { dbgmsg_printf("}\n"); return '}'; }
"("       { dbgmsg_printf("(\n"); return '('; }
")"       { dbgmsg_printf(")\n"); return ')'; }
"="       { dbgmsg_printf("=\n"); return '='; }
([!#$%\^\&\*\+-=]+|[a-zA-Z_][a-zA-Z_0-9]*) { dbgmsg_printf("ID : %s\n", yytext); return ID; }
.+        { dbgmsg_printf("ID : %s\n", yytext); return ID; }
%%
void dbgmsg_printf(char *format, ...) {
  if(_bDebugFlag == 1) {
    printf(format);
  }
}

int yywrap() {
  return 0;
}

void main() {
  yylex();
}
