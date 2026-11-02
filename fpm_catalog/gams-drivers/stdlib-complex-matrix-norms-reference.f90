! Independent MIT consumer; see licenses/grids-spectra-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64, int32
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_linalg, only: mnorm, linalg_state_type
   implicit none

   complex(real64),allocatable :: a(:,:),batch(:,:,:),saved(:,:)
   real(real64),allocatable :: magnitudes(:,:),norms(:)
   real(real64) :: one,inf,fro
   integer :: m,n,k,i,j,t,count
   count=0
   do m=1,6
      do n=1,6
         allocate(a(m,n),batch(m,n,3),magnitudes(m,n))
         do k=0,2
            do j=1,n
               do i=1,m
                  t=k*(mod(i*i+3*j+i*j,13)-6)
                  a(i,j)=cmplx(3._real64,4._real64,real64)*real(t,real64)/8
                  magnitudes(i,j)=5._real64*abs(t)/8
               end do
            end do
            saved=a; one=maxval(sum(magnitudes,dim=1)); inf=maxval(sum(magnitudes,dim=2))
            fro=sqrt(sum(magnitudes**2))
            call check(mnorm(a,1),one); call check(mnorm(a,'1'),one)
            call check(mnorm(a,'inf'),inf); call check(mnorm(a,huge(0)),inf)
            call check(mnorm(a),fro); call check(mnorm(a,'Frobenius'),fro)
            batch(:,:,1)=a; batch(:,:,2)=2*a; batch(:,:,3)=-a
            norms=mnorm(batch,'inf',dim=[1,2])
            call check(norms(1),inf); call check(norms(2),2*inf); call check(norms(3),inf)
            if(any(a/=saved)) error stop 'Norm input preservation'
            count=count+1
         end do
         deallocate(a,batch,magnitudes)
      end do
   end do
   print '(a,i0)', 'Complex rectangular one/infinity/Frobenius norm matrices: ',count
   print '(a)', 'PASS stdlib-complex-matrix-norms-reference'
contains
   subroutine check(actual,expected)
      real(real64),intent(in) :: actual,expected
      if(.not.ieee_is_finite(actual)) error stop 'Nonfinite result'
      if(abs(actual-expected)>2.e-10_real64*max(1._real64,abs(expected))) error stop 'Independent reference'
   end subroutine
   subroutine checkz(actual,expected)
      complex(real64),intent(in) :: actual,expected
      call check(real(actual,real64),real(expected,real64))
      call check(aimag(actual),aimag(expected))
   end subroutine
   subroutine check_matrix(actual,expected)
      complex(real64),intent(in) :: actual(:,:),expected(:,:)
      integer :: i,j
      if(any(shape(actual)/=shape(expected))) error stop 'Matrix shape'
      do j=1,size(actual,2)
         do i=1,size(actual,1)
            call checkz(actual(i,j),expected(i,j))
         end do
      end do
   end subroutine
   function identity(n) result(a)
      integer,intent(in) :: n
      complex(real64) :: a(n,n)
      integer :: i
      a=0
      do i=1,n
         a(i,i)=1
      end do
   end function
   function unitary(n,k) result(q)
      integer,intent(in) :: n,k
      complex(real64) :: q(n,n),v(n)
      real(real64) :: denominator
      integer :: i,j
      do i=1,n
         v(i)=cmplx(real(i,real64),real(mod(i+k,4)-2,real64),real64)
      end do
      denominator=real(dot_product(v,v),real64)
      q=identity(n)
      do j=1,n
         do i=1,n
            q(i,j)=q(i,j)-2*v(i)*conjg(v(j))/denominator
         end do
      end do
      call check_matrix(matmul(conjg(transpose(q)),q),identity(n))
   end function
end program
