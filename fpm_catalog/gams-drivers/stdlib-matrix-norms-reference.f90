! Independent MIT consumer; see licenses/factorization-rules-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_linalg, only: mnorm,linalg_state_type
   implicit none
   type(linalg_state_type) :: state
   real(real64),allocatable :: a(:,:)
   real(real64) :: one,inf,fro,total,actual,expected
   integer :: m,n,t,i,j,checks
   checks=0
   do m=1,5
      do n=1,7
         allocate(a(m,n))
         do t=0,4
            do j=1,n
               do i=1,m
                  a(i,j)=real(mod(5*i+3*j+t,17)-8,real64)/8
               end do
            end do
            if(t==0) a=0
            one=0
            inf=0
            fro=0
            do j=1,n
               total=0
               do i=1,m
                  total=total+abs(a(i,j))
                  fro=fro+a(i,j)*a(i,j)
               end do
               one=max(one,total)
            end do
            do i=1,m
               total=0
               do j=1,n
                  total=total+abs(a(i,j))
               end do
               inf=max(inf,total)
            end do
            fro=sqrt(fro)
            actual=mnorm(a,'1',err=state)
            expected=one
            call verify()
            actual=mnorm(a,'Inf',err=state)
            expected=inf
            call verify()
            actual=mnorm(a,'Frobenius',err=state)
            expected=fro
            call verify()
         end do
         deallocate(a)
      end do
   end do
   print '(a,i0)', '175 real matrices, including zeros; scalar-loop 1/infinity/Frobenius norm references: ',checks
   print '(a)', 'PASS stdlib-matrix-norms-reference'
contains
   subroutine verify()
      if(.not.state%ok().or..not.ieee_is_finite(actual)) error stop 'Matrix norm status'
      if(abs(actual-expected)>2.e-12_real64*max(1._real64,expected)) error stop 'Scalar-loop norm oracle'
      checks=checks+1
   end subroutine
end program
