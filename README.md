# c_compiler
## Должен поддерживать:  
### переменные типов:  
* `char`  
* `long long int`  
* `unsigned long long int`  
* `float (или double)`  
* `void`  

а также типы указателей  
инициализация всех переменных  
`[var_type] [var_name] [optional = [var_starting_value]]`

### функции:  
```
[return_type] [function_name] ([argument_type argument name]*) {
    [functioon body]
}
```
только функции с фиксированным прототипом

### указатели:  
для любой переменной доступны операции:  
* `*` (получение значения по адресу) и  
* `&` (получения адреса переменной)  

для любого указателя доступна операция  
`[some_int]` поддерживающая адресную арифметику  
адресная арифметика через + и - не доступна.

### массивы:  
статического размера заданные в compile time  
в виде:  
* `[array_ellement_type] [var_name] [arrray_lenght]`  
* `char * [var_name] = "[some_string]"`  

для первого доступна инициализация в виде [a,b,c, ... ],  
где a,b,c -- значения типа array_ellement_type

### инициализация численных значений и численные константы:  
для целых чисел:  
* `0x2313` -- hex constant  
* `0b11101101` -- binary constatn  
* `023423` -- octal constant  
* `123343` -- decimal constant  

все варианты могут иметь префикс "-" в случае знаковых  
для char  
`'a'` -- символьная константа  
для float  
* `15`  
* `15.`  
* `15.0`  
* `.01`  

экпоненциальной формы не будет

### ветвления:  
```
if ([condition]) {
  [body]
}
```  
else if и else с таким же синтаксисом  
no switches! they are realy stupid.

### циклы:  
```
for ([init];[condition];[increment]) {
  [body]
}
```  
```
while ([condition]) {
  [body]
}
```  
### строковые константы:  
`"*"`  
экранирование не поддерживается.