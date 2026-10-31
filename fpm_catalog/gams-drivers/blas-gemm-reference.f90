! Original D1b6 API driver. MIT: licenses/linear-algebra-api-drivers-MIT.txt.
program main
   use iso_fortran_env, only: dp=>real64
   use ieee_arithmetic, only: ieee_is_finite
   use blas, only: blas_gemm
   implicit none
   real(dp) :: base_a(3,2),base_b(2,4),initial(3,4),actual(3,4),expected(3,4)
   real(dp),allocatable :: a(:,:),b(:,:)
   real(dp),parameter :: alphas(*)=[1._dp,-2._dp,0._dp],betas(*)=[0._dp,.5_dp,-1._dp]
   real(dp) :: alpha,beta,error,maximum_error
   character,parameter :: options(*)=['N','T']
   integer :: i,j,k,ta,tb,mode,cases
   do i=1,3
      do k=1,2
         base_a(i,k)=real(2*i-3*k,dp)
      end do
      do j=1,4
         initial(i,j)=real(i-j,dp)/2
      end do
   end do
   do k=1,2
      do j=1,4
         base_b(k,j)=real(3*k-j,dp)
      end do
   end do
   maximum_error=0
   cases=0
   do ta=1,2
      do tb=1,2
         if(ta==1) then
            a=base_a
         else
            a=transpose(base_a)
         end if
         if(tb==1) then
            b=base_b
         else
            b=transpose(base_b)
         end if
         do mode=1,3
            alpha=alphas(mode); beta=betas(mode)
            expected=beta*initial
            ! Independent scalar loops; no MATMUL or another BLAS call supplies the reference.
            do i=1,3
               do j=1,4
                  do k=1,2
                     expected(i,j)=expected(i,j)+alpha*base_a(i,k)*base_b(k,j)
                  end do
               end do
            end do
            actual=initial
            call blas_gemm(options(ta),options(tb),3,4,2,alpha,a,size(a,1),b,size(b,1),beta,actual,3)
            if(.not.all(ieee_is_finite(actual))) error stop 'nonfinite GEMM result'
            error=maxval(abs(actual-expected))/max(1._dp,maxval(abs(expected)))
            maximum_error=max(maximum_error,error)
            if(error>1.e-12_dp) error stop 'GEMM scalar-loop reference'
            cases=cases+1
            if(ta==1 .and. tb==1 .and. mode==1) then
               print '(a)', '3-by-2 times 2-by-4 matrix product:'
               do i=1,3
                  print '(4f12.4)',actual(i,:)
               end do
            end if
         end do
      end do
   end do
   if(cases/=12) error stop 'case count'
   print '(a,i0)', 'Transpose/scaling combinations checked: ',cases
   print '(a,es12.4)', 'Maximum scaled error: ',maximum_error
   print '(a)', 'PASS blas-gemm-reference'
end program
