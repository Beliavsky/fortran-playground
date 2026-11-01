! Independent MIT API consumer; see licenses/state-ten-drivers-MIT.txt.
program containers_reference
   use qvector_m, only: qvector_t,QVECTOR_RESIZE_LINEAR
   use qhashtbl_m, only: qhashtbl_t
   implicit none
   integer :: cycle,i,j,n,value,reference(96),mapped(17),checks
   logical :: found,present(17)
   character(16) :: key
   checks=0
   do cycle=1,8
      block
         type(qvector_t) :: vector
         type(qhashtbl_t) :: table
         call vector%new(2,storage_size(value)/8,QVECTOR_RESIZE_LINEAR)
         call table%new(range=3,size_data=storage_size(value)/8)
         present=.false.; mapped=0; n=0
         do i=1,96
            value=modulo(i*(cycle+2),31)-15
            call vector%addlast(value,found)
            if (.not.found) error stop 'C vector append'
            n=n+1; reference(n)=value
            if (modulo(i,7)==0) then
               j=1+modulo(i*3,n); reference(j)=-i
               call vector%setat(j,reference(j),found)
               if (.not.found) error stop 'C vector edit'
            end if
            do j=1,n
               call vector%getat(j,value,found)
               if (.not.found .or. value/=reference(j)) error stop 'C vector indexed reference'
               checks=checks+1
            end do
            j=1+modulo(i*5,17); write(key,'(a,i0)') 'key_',j
            mapped(j)=i-100*cycle; present(j)=.true.
            call table%put(trim(key),mapped(j),success=found)
            if (.not.found) error stop 'C map insertion'
            do j=1,17
               write(key,'(a,i0)') 'key_',j
               call table%get(trim(key),value,found)
               if (found .neqv. present(j)) error stop 'C map presence reference'
               if (found) then
                  if (value/=mapped(j)) error stop 'C map replacement reference'
               end if
               checks=checks+1
            end do
         end do
         do i=1,96
            call vector%popfirst(value,found)
            if (.not.found .or. value/=reference(i)) error stop 'C vector pop reference'
            if (vector%size()/=96-i) error stop 'C vector pop size'
            checks=checks+1
         end do
         call vector%clear(); call table%clear()
         if (vector%size()/=0 .or. table%size()/=0) error stop 'C containers clear'
         call vector%addlast(cycle,found)
         if (.not.found) error stop 'C vector reuse'
         call vector%getat(1,value,found)
         if (.not.found .or. value/=cycle) error stop 'C vector reused value'
         call table%put('reused',cycle,success=found)
         if (.not.found) error stop 'C map reuse'
         call table%get('reused',value,found)
         if (.not.found .or. value/=cycle) error stop 'C map reused value'
         checks=checks+2
      end block
   end do
   print '(a,i0)', 'Eight vector/map traces; exact value/presence references: ',checks
   print '(a)', 'C-backed growth, indexed edits, FIFO removal, map insertion/replacement, absent keys and clear/reuse.'
   print '(a)', 'Integer payloads only; iterator order, object copying, all C ownership paths and thread safety unverified.'
   print '(a)', 'PASS qcontainers-state-reference'
end program
