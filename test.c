void * some_func(char a) {}



int main(int argc, char** argv) {
    int n, i, some_int = 0x7, some_int_2;
    char b = 'c';
    char * g = "sdfsdgfgf";
    float f = 1.343;
    unsigned fact = 1;
    printf("Enter an integer: ");
    scanf("%d", &n);

    // shows error if the user enters a negative integer
    if (n < 0) {
        printf("Error! Factorial of a negative number doesn't exist.");
    } else {
        for (i = 1; i <= n; ++i) {
            fact = fact * i;
        }
        printf("Factorial of %d = %llu", n, fact);
    }
    return 0;
}