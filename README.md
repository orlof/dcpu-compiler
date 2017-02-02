# dcpu-compiler
*Optimizing DCPU assembler in python*

<pre>
usage: compiler.py [-h] [--doc] [--debug] [--optimize] [--boot] [--verbose]
                   [--org ORG]
                   input [output]

compiler for DCPU assembler

positional arguments:
  input       source code (.dasm16)
  output      binary file (.bin)

optional arguments:
  -h, --help  show this help message and exit
  --doc       create documentation from doc directives
  --debug     create debugger info *.dbg see http://github.com/orlof/dcpu-
              debugger
  --optimize  optimize local jumps with xor, add and sub - may clear EX
  --boot      create also TC *.boot disk
  --verbose   print every character from lexer
  --org ORG   destination address
</pre>

### Preprocessor directives

#### #define

 - No multiline or function defines
 - Nested defines ok

#### #include

supported

#### #doc

Command line option --doc creates .txt file that collects all doc string and
prepends those with address.

<pre>
set a, 1
#doc HERE WE ARE
set b, 2
#doc ..and again
</pre>

<pre>
0x0001: HERE WE ARE
0x0002: ..and again
</pre>

Strictly speaking doc is not implemented in proprocessor as later
compilation passes modify memory locations.

### Special directives

#### DAT

DAT directive supports list of items that can be
 - string literals
 - expression of chars, integers, defined macros and labels
   - operations: +, -, * and /

All of the following are valid values:

<pre>
  #define ZERO 0

:data_label
  DAT 6, "abcde", ZERO, data_label + 1, 'A' + 20
</pre>

String literals support following escape sequences:

<table border="1" bgcolor="#dddddd">
<tr>
  <th>Escape sequence</th>
  <th>Hex value</th>
  <th>Character represented</th>
</tr>
<tr>
  <td>\\</td>
  <td>0x5c</td>
  <td>Backslash</td>
</tr>
<tr>
  <td>\b</td>
  <td>0x0010</td>
  <td>Backspace</td>
</tr>
<tr>
  <td>\t</td>
  <td>0x0010</td>
  <td>Horizontal tab</td>
</tr>
<tr>
  <td>\r</td>
  <td>0x0011</td>
  <td>Carriage return</td>
</tr>
<tr>
  <td>\n</td>
  <td>0x0011</td>
  <td>Newline (aka linefeed, carriage return in DCPU\r)</td>
</tr>
<tr>
  <td>\0</td>
  <td>0x0000</td>
  <td>Zero</td>
</tr>
<tr>
  <td>\'</td>
  <td>0x0027</td>
  <td>Single quotation mark</td>
</tr>
<tr>
  <td>\"</td>
  <td>0x0022</td>
  <td>Double quotation mark</td>
</tr>
<tr>
  <td>\xhh</td>
  <td>0x0000-0x00ff</td>
  <td>The character whose numerical value is given by hh interpreted as a hexadecimal number</td>
</tr>
</table>



#### JMP

JMP is an optimizing instruction for modifying PC with literal value.

    set PC, 0xbeef
    jmp 0xbeef

JMP can be used with any of the a-operand formats, but it functions as standard set operator.

    jmp [a + 5]
    set PC, [a + 5]

With literal a-operand type JMP compiles into one of the following instructions
(in priority order):

<table border="1" bgcolor="#dddddd">
<tr>
  <th>Instruction</th>
  <th>Range</th>
  <th>Memory</th>
  <th>Cycles</th>
  <th>Notes</th>
</tr>
<tr>
  <td>SET PC, 0x10</td>
  <td>0x0000-0x001e, 0xffff</td>
  <td>1</td>
  <td>1</td>
  <td>Set with short form literal</td>
</tr>
<tr>
  <td>XOR PC, 0x10</td>
  <td>local 5 bit segment in memory</td>
  <td>1</td>
  <td>1</td>
  <td>Cannot jump to 0x1f in local segment</td>
</tr>
<tr>
  <td>ADD PC, 0x10</td>
  <td>0x00-0x1e words forward</td>
  <td>1</td>
  <td>2</td>
  <td>Zeroes EX flag!</td>
</tr>
<tr>
  <td>SUB PC, 0x10</td>
  <td>0x00-0x1e words backward</td>
  <td>1</td>
  <td>2</td>
  <td>Zeroes EX flag!</td>
</tr>
<tr>
  <td>SET PC, 0x1000</td>
  <td>0x0000-0xffff</td>
  <td>2</td>
  <td>2</td>
  <td>Standard set can jump anywhere in memory</td>
</tr>
</table>

#### Single line IFx

Compiler also supports format where IFx and "then" instructions are
written in single line:

<pre>
  IFE a, 5 SET a, 6
</pre>

### Output Options

#### Default

Compiler always outputs the compiled binary image as .bin file that.
If --org command line option is specified, then all the jump addresses (etc)
are modified accordingly, but the binary output contains only the compiled
code i.e. No zeros for 0-org addresses.

#### Boot disk

--boot option outputs Techcompliant boot disk image (floppy).

Boot disk will have filename extension ".boot". It contains the standard BBOS
boot code in sector 0
[https://github.com/MadMockers/DCPUBootloader/tree/master/util]
and compiled code in the following sectors.

#### Debug Information

--debug option outputs debug information for [https://github.com/orlof/dcpu-debugger].

Debug information is stored with file extension ".dbg""

### Optimizations

#### Short literals

Short literals are always used instead of long literals. Works also with
defined values, address labels and expressions.

#### IFx swap

If "IFx" statement contains short literal as b-operand then a and b are
swapped to be able to use short literal optimization.

#### Local jumps

With --optimize command line option all "set pc, 0xbeef" -style instructions
are optimized as they were "jmp 0xbeef" instructions. This may break
applications that trust in EX value preservation during jumps.
