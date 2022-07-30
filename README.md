# Boolean Retrieval
**Assignment-1 for the course Information Retrieval (CS F469)**

Group members: <br>
Ankita Behera (2019A7PS0075H) <br>
Pranav Balaji (2019A7PS0040H) <br>
Ojashvi Tarunabh (2019A7PS0025H) <br>

## How to use
### Windows
From root directory run `python src`<br>
### Linux
From root directory run `py3 src`<br>
#### Query Format
Valid boolean operators are **AND**, **OR** and **NOT**. They are not case sensitive. Every two operands should be enclosed in parentheses. <br>
```
(Brutus and Calpurnia) or Anthony
(Brutus OR Calpurnia) OR NOT Anthony
```
#### Wildcard Queries
Only single wildcard per term is supported. <br>
```
(Brut* AND Ant*ny) OR *purnia
```



