# Boolean Retrieval
 Assignment-1 for the course Information Retrieval (CS F469)

Group members:
Ankita Behera (2019A7PS0075H) <br>
Pranav Balaji (2019A7PS0040H) <br>
Ojashvi Tarunabh (2019A7PS0025H) <br>

## How to use
### Windows
From root directory type `python src`<br>
### Linux
From root directory type `py3 src`<br>
#### Query Format
Valid boolean operators are AND, OR and NOT and are not case sensitive. Every two operands should be enclosed in parentheses. <br>
```
(Brutus and Calpurnia) or Anthony
(Brutus OR Calpurnia) OR NOT Anthony
```
#### Wildcard Queries
Single wildcard queries are supported. <br>
```
(Brut&ast; AND Ant&ast;ny) OR &ast;purnia
```



