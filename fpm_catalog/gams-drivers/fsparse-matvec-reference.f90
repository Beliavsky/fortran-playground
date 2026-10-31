! Original D1b4 API driver. MIT: licenses/linear-algebra-api-drivers-MIT.txt.
program main
   use fsparse, only: COO_dp,CSR_dp,dense2coo,coo2csr,matvec
   use fsparse_constants, only: dp
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   type(COO_dp) :: coo
   type(CSR_dp) :: csr
   real(dp) :: a(4,3),vectors(3,3),x(3),initial(4),product(4),expected(4),ycoo(4),ycsr(4)
   integer :: i,j,v,mode,repetition,calls
   a=reshape([2._dp,0._dp,0._dp,-1._dp, 0._dp,3._dp,0._dp,0._dp, &
      4._dp,0._dp,0._dp,5._dp],[4,3])
   vectors(:,1)=[1._dp,-2._dp,3._dp]
   vectors(:,2)=[0._dp,1._dp,-1._dp]
   vectors(:,3)=0
   call dense2coo(a,coo)
   call coo2csr(coo,csr)
   calls=0
   do v=1,3
      x=vectors(:,v)
      product=0
      do i=1,4
         do j=1,3
            product(i)=product(i)+a(i,j)*x(j)
         end do
      end do
      do mode=0,1
         initial=real(mode,dp)*[.5_dp,-1._dp,7._dp,2._dp]
         ycoo=initial
         ycsr=initial
         do repetition=1,2
            ! This API accumulates y := y+A*x. Repeating the call must add again.
            call matvec(coo,x,ycoo)
            call matvec(csr,x,ycsr)
            expected=initial+repetition*product
            call check(ycoo,expected)
            call check(ycsr,expected)
            calls=calls+2
         end do
      end do
      print '(a,i0,a,4f10.3)', 'A*x for vector ',v,': ',product
   end do
   if(calls/=24) error stop 'case count'
   print '(a,i0)', 'COO/CSR accumulated products checked: ',calls
   print '(a)', 'Rectangular 4-by-3 matrix includes an empty row; zero/nonzero output and zero input checked.'
   print '(a)', 'PASS fsparse-matvec-reference'
contains
   subroutine check(actual,reference)
      real(dp),intent(in) :: actual(:),reference(:)
      if(.not.all(ieee_is_finite(actual))) error stop 'nonfinite sparse result'
      if(maxval(abs(actual-reference))>1.e-12_dp) error stop 'sparse scalar-loop reference'
   end subroutine
end program
