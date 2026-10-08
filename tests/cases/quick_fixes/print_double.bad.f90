program main
implicit none
integer, parameter :: n = 3
real :: x(n) = [1.0, 2.0, 3.0]
print "(i0, *(1x,f0.4))" n, sum(x)/n, sum(x**2)/n, minval(x), maxval(x)
end program
