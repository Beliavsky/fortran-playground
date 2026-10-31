! Independent API consumer; MIT: licenses/products-status-drivers-MIT.txt.
program exact_products
   use kinds, only: rk
   use fordot, only: fdot => dot_product
   use, intrinsic :: iso_fortran_env, only: int64
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, parameter :: lengths(*) = [1,7,8,17,64]
   character(2), parameter :: methods(*) = ['m1','m2','m3','m4']
   real(rk), allocatable :: u(:),v(:)
   integer(int64) :: numerator,a,b
   real(rk) :: expected,actual
   integer :: l,n,pattern,i,method,block,blocks(3),calls
   calls = 0
   do l = 1,size(lengths)
      n = lengths(l)
      allocate(u(n),v(n))
      blocks = [1,3,n]
      do pattern = 1,3
         numerator = 0_int64
         do i = 1,n
            select case(pattern)
            case(1)
               a = mod(7*i,23)-11
               b = mod(11*i,19)-9
            case(2)
               a = (-1)**i*(mod(i,5)+1)
               b = 3
            case(3)
               a = 0
               b = mod(i,13)-6
            end select
            u(i) = real(a,rk)/8
            v(i) = real(b,rk)/4
            numerator = numerator+a*b
         end do
         expected = real(numerator,rk)/32
         actual = fdot(u,v)
         call check(actual,expected)
         do method = 1,size(methods)
            actual = fdot(u,v,option=methods(method))
            call check(actual,expected)
            do block = 1,size(blocks)
               if (blocks(block) > n) cycle
               if (block > 1) then
                  if (any(blocks(:block-1) == blocks(block))) cycle
               end if
               actual = fdot(u,v,option=methods(method),nblock=blocks(block))
               call check(actual,expected)
            end do
         end do
         print '(a,i0,a,i0,a,f12.5)', 'Length=',n,' pattern=',pattern,' exact dot product=',expected
      end do
      deallocate(u,v)
   end do
   if (calls /= 231) error stop 'dot product call count'
   print '(a)', '231 exact results checked: default and m1..m4, including unequal blocks and zero products.'
   print '(a)', 'PASS fordot-exact-reference'
contains
   subroutine check(actual,expected)
      real(rk), intent(in) :: actual,expected
      if (.not. ieee_is_finite(actual)) error stop 'nonfinite dot product'
      if (actual /= expected) error stop 'exact int64 numerator reference'
      calls = calls+1
   end subroutine check
end program exact_products
