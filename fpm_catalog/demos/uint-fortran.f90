program unsigned_boundaries
   use iso_fortran_env, only: int64
   use unsigned_m
   use int_m, only: int
   implicit none
   type(uint32)::a,b,result
   type(uint16)::small
   integer(int64),parameter::modulus=4294967296_int64
   integer(int64)::expected
   a=2147483648_int64
   b=3
   result=a+b
   expected=2147483651_int64
   if(int(result)/=expected) error stop 'Addition across signed boundary failed'
   if(.not.(a>b)) error stop 'Unsigned comparison failed'
   print '(a,i0)', '2147483648 + 3 = ',int(result)
   a=modulus-1
   b=1
   result=a+b
   if(int(result)/=0_int64) error stop '32-bit addition did not wrap'
   result=b-a
   if(int(result)/=2_int64) error stop '32-bit subtraction did not wrap'
   a=-10
   if(int(a)/=modulus-10) error stop 'Negative assignment conversion failed'
   small=65535
   if(int(small)/=65535) error stop '16-bit upper boundary failed'
   small=small+1
   if(int(small)/=0) error stop '16-bit addition did not wrap'
   print '(a)', 'Verified 16/32-bit boundaries, wraparound and negative assignment.'
   print *, 'PASS uint-fortran'
end program unsigned_boundaries
