! Independent MIT consumer; see licenses/ordering-runge-ten-drivers-MIT.txt.
program main
   use iso_fortran_env,only:wp=>real64
   use M_orderpack,only:median,medianval,medianloc
   implicit none
   real(wp),allocatable::x(:),sorted(:),work(:),ref(:)
   integer,allocatable::indices(:),counts(:)
   real(wp)::t,expected
   integer::n,i,j,k,pattern,nu,nref,loc,cases
   cases=0
   do n=1,65
      allocate(x(n),sorted(n),work(n),ref(n),indices(n),counts(n))
      do pattern=1,5
         do i=1,n
            select case(pattern)
            case(1)
               x(i)=real(modulo(17*i+3*n,23)-11,wp)/4
            case(2)
               x(i)=real(i/3,wp)/4
            case(3)
               x(i)=-real(i/3,wp)/4
            case(4)
               x(i)=-0.75_wp
            case(5)
               x(i)=real(modulo(37*(i-1),67)-33,wp)/4
            end select
         end do
         sorted=x
         call insertion_sort(sorted)
         expected=(sorted((n+1)/2)+sorted(n/2+1))/2
         if(median(x)/=expected) error stop 'Averaged median'
         expected=sorted((n+1)/2)
         if(medianval(x)/=expected) error stop 'Lower median value'
         call medianloc(x,loc)
         if(loc<1.or.loc>n) error stop 'Median location bounds'
         if(x(loc)/=expected) error stop 'Lower median location'
         cases=cases+1
      end do
      deallocate(x,sorted,work,ref,indices,counts)
   end do
   print '(a,i0)', 'Checked finite REAL64 data sets: ',cases
   print '(a)', 'Arithmetic central-pair median versus lower-middle medianval/medianloc conventions; odd and even sizes checked.'
   print '(a)', 'PASS orderpack-median-conventions-reference'
contains
   subroutine insertion_sort(a)
      real(wp),intent(inout)::a(:)
      real(wp)::v
      integer::p,q
      do p=2,size(a)
         v=a(p);q=p-1
         do while(q>=1)
            if(a(q)<=v) exit
            a(q+1)=a(q);q=q-1
         end do
         a(q+1)=v
      end do
   end subroutine
end program
