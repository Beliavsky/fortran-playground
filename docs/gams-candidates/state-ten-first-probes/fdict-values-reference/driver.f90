! Independent MIT API consumer; see licenses/state-ten-drivers-MIT.txt.
program dictionary_reference
   use dictionary
   use, intrinsic :: iso_fortran_env, only: real64
   implicit none
   type(dictionary_t) :: table
   integer :: cycle,i,value,array(3),checks
   real(real64) :: real_value
   character(32) :: key,text,expected
   logical :: found
   checks=0
   do cycle=1,8
      table=('base'.kv.cycle)
      do i=1,48
         write(key,'(a,i0)') 'key_',i
         select case(modulo(i,4))
         case(0)
            table=table//(trim(key).kv.(i-100*cycle))
         case(1)
            table=table//(trim(key).kv.(real(i-cycle,real64)/8))
         case(2)
            write(text,'(a,i0,a,i0)') 'value_',cycle,'_',i
            table=table//(trim(key).kv.trim(text))
         case(3)
            array=[i,cycle,-i]; table=table//(trim(key).kv.array); array=999
         end select
      end do
      do i=48,1,-1
         write(key,'(a,i0)') 'key_',i
         select case(modulo(i,4))
         case(0)
            call assign(value,table,trim(key),success=found)
            if (.not.found .or. value/=i-100*cycle) error stop 'dictionary integer reference'
         case(1)
            call assign(real_value,table,trim(key),success=found)
            if (.not.found .or. real_value/=real(i-cycle,real64)/8) error stop 'dictionary real reference'
         case(2)
            call assign(text,table,trim(key),success=found)
            write(expected,'(a,i0,a,i0)') 'value_',cycle,'_',i
            if (.not.found .or. text/=expected) error stop 'dictionary text reference'
         case(3)
            call assign(array,table,trim(key),success=found)
            if (.not.found .or. any(array/=[i,cycle,-i])) error stop 'dictionary owned array reference'
         end select
         checks=checks+1
      end do
      do i=2,48,2
         write(key,'(a,i0)') 'key_',i
         call delete(table,trim(key))
      end do
      ! Odd keys survive deletions elsewhere in the hash-linked structure.
      do i=1,48,4
         write(key,'(a,i0)') 'key_',i
         call assign(real_value,table,trim(key),success=found)
         if (.not.found .or. real_value/=real(i-cycle,real64)/8) error stop 'dictionary survivor reference'
         checks=checks+1
      end do
      call assign(value,table,'base',success=found)
      if (.not.found .or. value/=cycle) error stop 'dictionary base reference'
      checks=checks+1
      call delete(table)
   end do
   print '(a,i0)', 'Eight 49-key dictionaries; exact typed lookup references: ',checks
   print '(a)', 'Integer/REAL64/text/array values, owned array copies, reverse lookup order and deletion survivors.'
   print '(a)', 'Missing/type-mismatched lookups, duplicate-key policy, dictionary copying and all hash collisions unverified.'
   print '(a)', 'PASS fdict-values-reference'
end program
