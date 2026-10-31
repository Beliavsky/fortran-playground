! Independent API consumer; MIT: licenses/inverse-tvd-drivers-MIT.txt.
program inverse_factor_reference
   use, intrinsic :: iso_fortran_env, only: dp => real64
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   use linalg_fortran, only: linalg
   implicit none
   integer, parameter :: sizes(*) = [1,2,3,4,5,8]
   real(dp), parameter :: lower_values(*) = [-.5_dp,.25_dp],upper_values(*) = [-.25_dp,.5_dp]
   real(dp), parameter :: scales(*) = [.5_dp,1._dp,8._dp]
   real(dp), allocatable :: a(:,:),expected(:,:),inverse(:,:),d(:),lower(:,:),upper(:,:),row(:)
   real(dp) :: det_expected,ell,up,fac,max_inverse_error,max_residual,max_det_error
   real(dp) :: singular2(2,2),singular3(3,3)
   integer :: dimension,il,iu,is,n,i,j,k,cases
   cases = 0
   max_inverse_error = 0._dp
   max_residual = 0._dp
   max_det_error = 0._dp
   do dimension = 1,size(sizes)
      n = sizes(dimension)
      allocate(a(n,n),expected(n,n),d(n),lower(n,n),upper(n,n),row(n))
      d = [(real((-1)**(i+1)*(i+1),dp),i=1,n)]
      do il = 1,2
         ell = lower_values(il)
         do iu = 1,2
            up = upper_values(iu)
            lower = 0._dp
            upper = 0._dp
            do i = 1,n
               lower(i,i) = 1._dp
               upper(i,i) = 1._dp
               if (i < n) then
                  lower(i+1,i) = ell
                  upper(i,i+1) = up
               end if
            end do
            do is = 1,size(scales)
               fac = scales(is)
               a = 0._dp
               expected = 0._dp
               do j = 1,n
                  do i = 1,n
                     do k = 1,n
                        a(i,j) = a(i,j)+fac*lower(i,k)*d(k)*upper(k,j)
                     end do
                     do k = max(i,j),n
                        expected(i,j) = expected(i,j)+(-up)**(k-i)*(-ell)**(k-j)/(fac*d(k))
                     end do
                  end do
               end do
               det_expected = product(d)*fac**n
               call check
               if (n > 1) then
                  row = a(1,:)
                  a(1,:) = a(n,:)
                  a(n,:) = row
                  row = expected(:,1)
                  expected(:,1) = expected(:,n)
                  expected(:,n) = row
                  det_expected = -det_expected
                  call check
               end if
            end do
         end do
      end do
      deallocate(a,expected,d,lower,upper,row)
   end do
   singular2 = reshape([1._dp,2._dp,2._dp,4._dp],[2,2])
   if (linalg%det(singular2) /= 0) error stop 'singular 2x2 determinant'
   if (linalg%inv(singular2)) error stop 'singular 2x2 accepted'
   singular3 = 0._dp
   singular3(1,1) = 1._dp
   singular3(3,3) = 2._dp
   if (linalg%det(singular3) /= 0) error stop 'singular 3x3 determinant'
   if (linalg%inv(singular3)) error stop 'singular 3x3 accepted'
   if (cases /= 132) error stop 'matrix fixture count'
   print '(a)', '132 scaled/permuted known-factor matrices, dimensions 1,2,3,4,5,8; two singular rejections.'
   print '(a,es12.4)', 'Maximum inverse error / max(1,maxabs(reference)): ',max_inverse_error
   print '(a,es12.4)', 'Maximum independently accumulated left/right inverse residual: ',max_residual
   print '(a,es12.4)', 'Maximum determinant relative error: ',max_det_error
   print '(a)', 'PASS linalg-inverse-factor-reference'
contains
   subroutine check
      real(dp) :: determinant,error,left,right,identity
      inverse = a
      if (.not. linalg%inv(inverse)) error stop 'nonsingular inverse status'
      if (.not. all(ieee_is_finite(inverse))) error stop 'nonfinite inverse'
      error = maxval(abs(inverse-expected))/max(1._dp,maxval(abs(expected)))
      max_inverse_error = max(max_inverse_error,error)
      if (error > 2.e-12_dp) error stop 'closed-form inverse'
      do j = 1,n
         do i = 1,n
            identity = 0._dp
            if (i == j) identity = 1._dp
            left = -identity
            right = -identity
            do k = 1,n
               left = left+a(i,k)*inverse(k,j)
               right = right+inverse(i,k)*a(k,j)
            end do
            max_residual = max(max_residual,abs(left),abs(right))
            if (max(abs(left),abs(right)) > 5.e-12_dp) error stop 'left/right inverse residual'
         end do
      end do
      determinant = linalg%det(a)
      if (.not. ieee_is_finite(determinant)) error stop 'nonfinite determinant'
      error = abs(determinant/det_expected-1)
      max_det_error = max(max_det_error,error)
      if (error > 2.e-12_dp) error stop 'factor/permutation determinant'
      cases = cases+1
   end subroutine check
end program inverse_factor_reference
