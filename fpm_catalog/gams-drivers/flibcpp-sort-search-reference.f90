! Independent MIT API consumer; see licenses/data-ten-drivers-MIT.txt.
program sort_search_reference
   use, intrinsic :: iso_c_binding, only: c_int32_t,c_int64_t,c_double
   use flc_algorithm, only: sort,binary_search
   implicit none
   integer :: n,pattern,i,j,key,temporary,position,fixtures,entries,queries
   integer :: reference(64),original(64)
   fixtures=0; entries=0; queries=0
   do n=0,64
      do pattern=1,4
         do i=1,n
            select case(pattern)
            case(1)
               reference(i)=i-32
            case(2)
               reference(i)=32-i
            case(3)
               reference(i)=modulo(7*i+3*n,27)-13
            case(4)
               reference(i)=(-1)**i*modulo(i,11)
            end select
         end do
         original(1:n)=reference(1:n)
         ! Independent insertion-sort oracle, not the C++ wrapper.
         do i=2,n
            temporary=reference(i); j=i-1
            do while(j>=1)
               if (reference(j)<=temporary) exit
               reference(j+1)=reference(j); j=j-1
            end do
            reference(j+1)=temporary
         end do
         block
            integer(c_int32_t), allocatable, target :: values(:)
            integer(c_int32_t) :: wanted
            allocate(values(n))
            ! Preserve each original input pattern independently of the oracle sort.
            do i=1,n
               values(i)=int(original(i),c_int32_t)
            end do
            call sort(values)
            do i=1,n
               if (values(i)/=int(reference(i),c_int32_t)) error stop 'sort reference differs'
            end do
            do key=-20,20
               wanted=int(key,c_int32_t)
               position=binary_search(values,wanted)
               if (any(reference(1:n)==key)) then
                  if (position<1 .or. position>n) error stop 'search present-key position'
                  if (values(position)/=wanted) error stop 'search present-key value'
               else
                  if (position/=0) error stop 'search absent-key sentinel'
               end if
               queries=queries+1
            end do
            fixtures=fixtures+1; entries=entries+n
         end block
         block
            integer(c_int64_t), allocatable, target :: values(:)
            integer(c_int64_t) :: wanted
            allocate(values(n))
            ! Preserve each original input pattern independently of the oracle sort.
            do i=1,n
               values(i)=5000000000_c_int64_t+int(original(i),c_int64_t)
            end do
            call sort(values)
            do i=1,n
               if (values(i)/=5000000000_c_int64_t+int(reference(i),c_int64_t)) error stop 'sort reference differs'
            end do
            do key=-20,20
               wanted=5000000000_c_int64_t+int(key,c_int64_t)
               position=binary_search(values,wanted)
               if (any(reference(1:n)==key)) then
                  if (position<1 .or. position>n) error stop 'search present-key position'
                  if (values(position)/=wanted) error stop 'search present-key value'
               else
                  if (position/=0) error stop 'search absent-key sentinel'
               end if
               queries=queries+1
            end do
            fixtures=fixtures+1; entries=entries+n
         end block
         block
            real(c_double), allocatable, target :: values(:)
            real(c_double) :: wanted
            allocate(values(n))
            ! Preserve each original input pattern independently of the oracle sort.
            do i=1,n
               values(i)=real(original(i),c_double)/8
            end do
            call sort(values)
            do i=1,n
               if (values(i)/=real(reference(i),c_double)/8) error stop 'sort reference differs'
            end do
            do key=-20,20
               wanted=real(key,c_double)/8
               position=binary_search(values,wanted)
               if (any(reference(1:n)==key)) then
                  if (position<1 .or. position>n) error stop 'search present-key position'
                  if (values(position)/=wanted) error stop 'search present-key value'
               else
                  if (position/=0) error stop 'search absent-key sentinel'
               end if
               queries=queries+1
            end do
            fixtures=fixtures+1; entries=entries+n
         end block
      end do
   end do
   if (fixtures/=780 .or. entries/=24960 .or. queries/=31980) error stop 'sort/search fixture counts'
   print '(a)', '780 typed array fixtures; 24960 sorted element references; 31980 present/absent search queries.'
   print '(a)', 'Lengths 0..64, duplicate and signed values; INT32, large INT64 and exact dyadic REAL64.'
   print '(a)', 'Search checks a valid duplicate match; NaNs, custom comparators and strided arrays unverified.'
   print '(a)', 'PASS flibcpp-sort-search-reference'
end program
