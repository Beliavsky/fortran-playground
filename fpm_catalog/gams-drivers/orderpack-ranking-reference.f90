! Independent API consumer; MIT: licenses/ranking-magic-drivers-MIT.txt.
program main
   use iso_fortran_env,only:int32,real32,real64
   use M_orderpack,only:rank
   implicit none
   integer,parameter::lengths(*)=[0,1,2,3,4,7,8,15,16,31,32,63,64,127]
   integer(int32),allocatable::a(:)
   integer::n,i,j,pattern,fixtures,calls,permutations
   fixtures=0; calls=0; permutations=0
   do n=1,7
      a=[(int(i,int32),i=1,n)]
      call permute(1)
   end do
   do j=1,size(lengths)
      n=lengths(j)
      if (allocated(a)) deallocate(a)
      allocate(a(n))
      do pattern=1,6
         do i=1,n
            select case(pattern)
            case(1)
               a(i)=i-n/2
            case(2)
               a(i)=n-i
            case(3)
               a(i)=7
            case(4)
               a(i)=mod(i,3)-1
            case(5)
               a(i)=(-1)**i*i
            case(6)
               a(i)=mod(37*i+11,17)-8
            end select
         end do
         call check_rank()
      end do
   end do
   if (permutations/=5913.or.fixtures/=5997.or.calls/=23988) error stop 'accounting'
   print '(a,i0)', 'Exhaustive permutations through length seven: ',permutations
   print '(a,i0,a,i0)', 'Total ranking fixtures: ',fixtures,'; overload calls: ',calls
   print '(a)', 'Integer32, real32, real64 and character keys; empty input, ties and boundary sizes.'
   print '(a)', 'Independent insertion-order reference; permutation integrity and input preservation.'
   print '(a)', 'PASS orderpack-ranking-reference'
contains
   recursive subroutine permute(first)
      integer,intent(in)::first
      integer::k,temp
      if (first>size(a)) then
         call check_rank()
         permutations=permutations+1
         return
      end if
      do k=first,size(a)
         temp=a(first); a(first)=a(k); a(k)=temp
         call permute(first+1)
         temp=a(first); a(first)=a(k); a(k)=temp
      end do
   end subroutine
   subroutine check_rank()
      integer::idx(size(a)),expected(size(a)),saved(size(a)),i,j,temp,mode
      real(real32)::single(size(a)),saved_single(size(a))
      real(real64)::double(size(a)),saved_double(size(a))
      character(len=4)::keys(size(a)),saved_keys(size(a))
      expected=a; saved=a
      do i=2,size(a)
         temp=expected(i); j=i-1
         do while(j>=1)
            if (expected(j)<=temp) exit
            expected(j+1)=expected(j); j=j-1
         end do
         expected(j+1)=temp
      end do
      single=real(a,real32)/8; double=real(a,real64)/8
      do i=1,size(a)
         write(keys(i),'(i4.4)') a(i)+512
      end do
      saved_single=single; saved_double=double; saved_keys=keys
      do mode=1,4
         idx=-1
         select case(mode)
         case(1)
            call rank(a,idx)
         case(2)
            call rank(single,idx)
         case(3)
            call rank(double,idx)
         case(4)
            call rank(keys,idx)
         end select
         if (any(idx<1).or.any(idx>size(a))) error stop 'index range'
         do i=1,size(a)
            if (count(idx==i)/=1) error stop 'indices are not a permutation'
         end do
         if (any(a(idx)/=expected)) error stop 'independent sorted-value reference'
         if (any(a/=saved).or.any(single/=saved_single).or.any(double/=saved_double) &
            .or.any(keys/=saved_keys)) error stop 'changed input'
         calls=calls+1
      end do
      fixtures=fixtures+1
   end subroutine
end program
