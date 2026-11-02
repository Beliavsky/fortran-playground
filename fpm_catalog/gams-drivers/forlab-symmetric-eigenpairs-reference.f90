! Independent MIT consumer; see licenses/forlab-statistics-ten-drivers-MIT.txt.
program main
   use iso_fortran_env,only:dp=>real64
   use ieee_arithmetic,only:ieee_is_finite
   use forlab,only:wp=>RPRE,eig
   implicit none
   real(wp),allocatable::a(:,:),l(:,:),v(:,:),u(:,:),w(:),result(:,:)
   real(dp),allocatable::reference(:,:),q(:,:),diagonal(:),product_reference(:,:)
   real(dp)::norm
   integer::n,m,i,j,k,status
   if(storage_size(0._wp)/=32) error stop 'Expected pinned Forlab REAL32 kind'
   do n=2,8
      allocate(q(n,n),diagonal(n),reference(n,n))
      norm=real(sum([(i*i,i=1,n)]),dp);q=identity(n)
      do j=1,n
         do i=1,n
            q(i,j)=q(i,j)-2*real(i*j,dp)/norm
         end do
         diagonal(j)=(-1._dp)**j*(1+real(j,dp)/4)
      end do
      reference=matmul(q*spread(diagonal,1,n),transpose(q));a=real(reference,wp)
      call eig(a,v,w)
      call matrix_check(matmul(transpose(v),v),identity(n))
      do j=1,n
         k=minloc(abs(real(w,dp)-diagonal(j)),dim=1)
         call check(w(k),diagonal(j))
         do i=1,n
            call check(dot_product(a(i,:),v(:,j)),real(w(j)*v(i,j),dp))
         end do
      end do
      deallocate(q,diagonal,reference,a,v,w)
   end do
   print '(a)', 'Seven analytically constructed symmetric eigensystems checked.'
   print '(a,i0)', 'Forlab real storage bits: ',storage_size(0._wp)
   print '(a)', 'PASS forlab-symmetric-eigenpairs-reference'
contains
   subroutine check(actual,reference)
      real(wp),intent(in)::actual
      real(dp),intent(in)::reference
      if(.not.ieee_is_finite(actual)) error stop 'Nonfinite result'
      if(abs(real(actual,dp)-reference)>3.e-5_dp*max(1._dp,abs(reference))) then
         print *, 'Actual, reference:',actual,reference
         error stop 'Independent reference'
      end if
   end subroutine
   subroutine matrix_check(actual,reference)
      real(wp),intent(in)::actual(:,:)
      real(dp),intent(in)::reference(:,:)
      integer::i,j
      if(any(shape(actual)/=shape(reference))) error stop 'Matrix shape'
      do j=1,size(actual,2)
         do i=1,size(actual,1)
            call check(actual(i,j),reference(i,j))
         end do
      end do
   end subroutine
   subroutine insertion_sort(x)
      real(dp),intent(inout)::x(:)
      real(dp)::v
      integer::i,j
      do i=2,size(x)
         v=x(i);j=i-1
         do while(j>=1)
            if(x(j)<=v) exit
            x(j+1)=x(j);j=j-1
         end do
         x(j+1)=v
      end do
   end subroutine
   function identity(n) result(a)
      integer,intent(in)::n
      real(dp)::a(n,n)
      integer::i
      a=0
      do i=1,n
         a(i,i)=1
      end do
   end function
end program
