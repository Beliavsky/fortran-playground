! Independent MIT consumer; see licenses/systems-spectra-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_linalg, only: solve_chol
   use stdlib_linalg_state, only: linalg_state_type
   implicit none
   real(real64),allocatable :: l(:,:),u(:,:),a(:,:),saved(:,:),b(:,:),x(:,:),expected(:,:),v(:)
   type(linalg_state_type) :: err
   integer :: n,t,i,j,k,side,calls
   calls=0
   do n=2,10
      allocate(l(n,n),u(n,n),a(n,n),saved(n,n),b(n,3),x(n,3),expected(n,3),v(n))
      do t=1,8
         l=0
         do i=1,n
            l(i,i)=1+real(i+t,real64)/8
            do j=1,i-1
               l(i,j)=real(mod(i+2*j+t,7)-3,real64)/16
            end do
            expected(i,:)=[1._real64,(-1._real64)**i*i/8,real(i*(n+1-i),real64)/16]
         end do
         u=transpose(l)
         a=matmul(l,u)
         saved=a
         b=0
         do i=1,n
            do j=1,n
               do k=1,3
                  b(i,k)=b(i,k)+a(i,j)*expected(j,k)
               end do
            end do
         end do
         do side=1,2
            call solve_chol(a,b,x,lower=side==1,err=err)
            if(.not.err%ok()) error stop 'SPD matrix solve status'
            call verify(x)
            call solve_chol(a,b(:,2),v,lower=side==1,err=err)
            if(.not.err%ok()) error stop 'SPD vector solve status'
            if(.not.all(ieee_is_finite(v))) error stop 'Nonfinite vector solution'
            if(maxval(abs(v-expected(:,2)))>3.e-12_real64*max(1._real64,maxval(abs(expected)))) &
               error stop 'Known vector solution'
            if(any(a/=saved)) error stop 'Input matrix preservation'
            calls=calls+2
         end do
      end do
      deallocate(l,u,a,saved,b,x,expected,v)
   end do
   print '(a,i0)', '72 SPD systems, vector and three-RHS matrix interfaces, lower/upper factors; solve calls: ',calls
   print '(a)', 'PASS stdlib-spd-solve-reference'
contains
   subroutine verify(y)
      real(real64),intent(in) :: y(:,:)
      if(.not.all(ieee_is_finite(y))) error stop 'Nonfinite matrix solution'
      if(maxval(abs(y-expected))>3.e-12_real64*max(1._real64,maxval(abs(expected)))) &
         error stop 'Manufactured SPD solution'
      if(maxval(abs(matmul(saved,y)-b))>3.e-12_real64*max(1._real64,maxval(abs(b)))) &
         error stop 'Original SPD residual'
   end subroutine
end program
