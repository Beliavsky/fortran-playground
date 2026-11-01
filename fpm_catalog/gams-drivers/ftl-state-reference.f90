! Independent MIT consumer; see licenses/interop-ten-drivers-MIT.txt.
program main
   use ftlDynArrayIntModule, only: ftlDynArrayInt
   use ftlHashMapStringIntModule, only: ftlHashMapStringInt
   implicit none
   type(ftlDynArrayInt) :: array
   type(ftlHashMapStringInt) :: map
   integer :: oracle(128),values(17),n,step,k,j,removed,trial,counted,checks
   logical :: present(17)
   character(12) :: key
   checks=0
   do trial=1,8
      call array%New()
      call map%New(10)
      n=0
      present=.false.
      values=0
      do step=1,128
         n=n+1
         oracle(n)=trial*step-37
         call array%PushBack(oracle(n))
         if(mod(step,3)==0) then
            removed=array%PopBack()
            if(removed/=oracle(n)) error stop 'Pop value'
            n=n-1
         end if
         if(array%Size()/=n) error stop 'Array size'
         if(any(array%data/=oracle(:n))) error stop 'Array oracle'
         k=mod(step*7,17)+1
         write(key,'(a,i0)') 'key-',k
         values(k)=trial*1000-step
         present(k)=.true.
         call map%Set(trim(key),values(k))
         if(mod(step,4)==0) then
            k=mod(step*3,17)+1
            write(key,'(a,i0)') 'key-',k
            if(present(k)) call map%Erase(trim(key))
            present(k)=.false.
         end if
         counted=0
         do j=1,17
            write(key,'(a,i0)') 'key-',j
            if(map%Has(trim(key)).neqv.present(j)) error stop 'Map presence'
            if(present(j)) then
               counted=counted+1
               if(map%Get(trim(key))/=values(j)) error stop 'Map value'
            end if
         end do
         if(map%Size()/=counted) error stop 'Map size'
         checks=checks+1
      end do
      do while(n>0)
         removed=array%PopBack()
         if(removed/=oracle(n)) error stop 'Drain order'
         n=n-1
      end do
      if(array%Size()/=0) error stop 'Drain size'
      call map%Delete()
      call array%Delete()
   end do
   print '(a,i0)', 'Independent array/map state checkpoints: ',checks
   print '(a)', 'PASS ftl-state-reference'
end program
