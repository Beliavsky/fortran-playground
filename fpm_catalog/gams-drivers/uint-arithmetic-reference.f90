! Independent API consumer; see licenses/unsigned-bitsets-drivers-MIT.txt.
program checked_unsigned_arithmetic
   use iso_fortran_env, only: int64
   use unsigned_m
   use int_m, only: int
   implicit none
   integer :: checks=0,pairs=0
   call check8()
   call check16()
   call check32()
   print '(a,i0)', 'Unsigned operand pairs: ',pairs
   print '(a,i0)', 'Exact integer checks: ',checks
   print '(a)', 'PASS uint-arithmetic-reference'
contains
   function fixtures(modulus) result(values)
      integer(int64), intent(in) :: modulus
      integer(int64) :: values(24)
      values=modulo([0_int64,1_int64,2_int64,3_int64,7_int64,15_int64,16_int64,31_int64,63_int64, &
         127_int64,128_int64,255_int64,modulus/2-1,modulus/2,modulus/2+1,modulus-3,modulus-2,modulus-1, &
         modulus/3,modulus/5,modulus/7,modulus/11,modulus/13,modulus/17],modulus)
   end function fixtures
   subroutine check(condition)
      logical, intent(in) :: condition
      if (.not.condition) error stop 'unsigned integer reference mismatch'
      checks=checks+1
   end subroutine check
   subroutine check8()
      type(uint8) :: a,b,result
      integer(int64), parameter :: modulus=256_int64
      integer(int64), parameter :: negatives(9)=[-1_int64,-2_int64,-127_int64,-128_int64,-255_int64, &
         -256_int64,-257_int64,-65536_int64,-4294967295_int64]
      integer(int64) :: values(24),x,y
      integer :: i,j
      values=fixtures(modulus)
      do i=1,size(values)
         x=values(i); a=x
         call check(int(a)==x)
         do j=1,size(values)
            y=values(j); b=y
            result=a+b; call check(int(result)==modulo(x+y,modulus))
            result=a-b; call check(int(result)==modulo(x-y,modulus))
            if (y/=0) then
               result=a/b; call check(int(result)==x/y)
            end if
            call check((a==b).eqv.(x==y))
            call check((a/=b).eqv.(x/=y))
            call check((a<b).eqv.(x<y))
            call check((a<=b).eqv.(x<=y))
            call check((a>b).eqv.(x>y))
            call check((a>=b).eqv.(x>=y))
            call check(int(a)==x.and.int(b)==y)
            pairs=pairs+1
         end do
      end do
      do i=1,size(negatives)
         a=negatives(i)
         call check(int(a)==modulo(negatives(i),modulus))
      end do
   end subroutine check8
   subroutine check16()
      type(uint16) :: a,b,result
      integer(int64), parameter :: modulus=65536_int64
      integer(int64), parameter :: negatives(9)=[-1_int64,-2_int64,-127_int64,-128_int64,-255_int64, &
         -256_int64,-257_int64,-65536_int64,-4294967295_int64]
      integer(int64) :: values(24),x,y
      integer :: i,j
      values=fixtures(modulus)
      do i=1,size(values)
         x=values(i); a=x
         call check(int(a)==x)
         do j=1,size(values)
            y=values(j); b=y
            result=a+b; call check(int(result)==modulo(x+y,modulus))
            result=a-b; call check(int(result)==modulo(x-y,modulus))
            if (y/=0) then
               result=a/b; call check(int(result)==x/y)
            end if
            call check((a==b).eqv.(x==y))
            call check((a/=b).eqv.(x/=y))
            call check((a<b).eqv.(x<y))
            call check((a<=b).eqv.(x<=y))
            call check((a>b).eqv.(x>y))
            call check((a>=b).eqv.(x>=y))
            call check(int(a)==x.and.int(b)==y)
            pairs=pairs+1
         end do
      end do
      do i=1,size(negatives)
         a=negatives(i)
         call check(int(a)==modulo(negatives(i),modulus))
      end do
   end subroutine check16
   subroutine check32()
      type(uint32) :: a,b,result
      integer(int64), parameter :: modulus=4294967296_int64
      integer(int64), parameter :: negatives(9)=[-1_int64,-2_int64,-127_int64,-128_int64,-255_int64, &
         -256_int64,-257_int64,-65536_int64,-4294967295_int64]
      integer(int64) :: values(24),x,y
      integer :: i,j
      values=fixtures(modulus)
      do i=1,size(values)
         x=values(i); a=x
         call check(int(a)==x)
         do j=1,size(values)
            y=values(j); b=y
            result=a+b; call check(int(result)==modulo(x+y,modulus))
            result=a-b; call check(int(result)==modulo(x-y,modulus))
            if (y/=0) then
               result=a/b; call check(int(result)==x/y)
            end if
            call check((a==b).eqv.(x==y))
            call check((a/=b).eqv.(x/=y))
            call check((a<b).eqv.(x<y))
            call check((a<=b).eqv.(x<=y))
            call check((a>b).eqv.(x>y))
            call check((a>=b).eqv.(x>=y))
            call check(int(a)==x.and.int(b)==y)
            pairs=pairs+1
         end do
      end do
      do i=1,size(negatives)
         a=negatives(i)
         call check(int(a)==modulo(negatives(i),modulus))
      end do
   end subroutine check32
end program checked_unsigned_arithmetic
