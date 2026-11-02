! Independent MIT consumer; see licenses/forlab-statistics-ten-drivers-MIT.txt.
program main
   use iso_fortran_env,only:dp=>real64
   use ieee_arithmetic,only:ieee_is_finite
   use forlab,only:wp=>RPRE,svd
   implicit none
   real(wp),allocatable::a(:,:),l(:,:),v(:,:),u(:,:),w(:),result(:,:)
   real(dp),allocatable::reference(:,:),q(:,:),diagonal(:),product_reference(:,:)
   real(dp)::norm
   integer::n,m,i,j,k,status
   if(storage_size(0._wp)/=32) error stop 'Expected pinned Forlab REAL32 kind'
   do n=2,6
      m=n+2;allocate(q(m,m),diagonal(n),reference(m,n))
      norm=real(sum([(i*i,i=1,m)]),dp);q=identity(m)
      do j=1,m
         do i=1,m
            q(i,j)=q(i,j)-2*real(i*j,dp)/norm
         end do
      end do
      diagonal=[(1+real(j,dp)/2,j=1,n)]
      reference=q(:,:n)*spread(diagonal,1,m);a=real(reference,wp)
      call svd(a,w,u,v,ierr=status)
      if(status/=0) error stop 'SVD status'
      call matrix_check(matmul(transpose(u),u),identity(n))
      call matrix_check(matmul(transpose(v),v),identity(n))
      result=matmul(u*spread(w,1,m),transpose(v))
      call matrix_check(result,reference)
      do j=1,n
         k=minloc(abs(real(w,dp)-diagonal(j)),dim=1);call check(w(k),diagonal(j))
      end do
      deallocate(q,diagonal,reference,a,u,v,w,result)
   end do
   print '(a)', 'Five tall SVDs: exact singular values and reconstruction checked.'
   print '(a,i0)', 'Forlab real storage bits: ',storage_size(0._wp)
   print '(a)', 'PASS forlab-tall-svd-reference'
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
