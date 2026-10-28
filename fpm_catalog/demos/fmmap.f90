! Persist a tiny array using an ordinary file, without large allocations.
program demo_fmmap
   use iso_c_binding, only: c_size_t, c_f_pointer, c_associated
   use fmmap
   implicit none
   type(fmmap_t) :: mapping
   integer, pointer :: values(:)
   integer :: i, unit
   integer(c_size_t) :: n

   n = 8_c_size_t
   call mapping%create(FMMAP_NEW,'mapped-array.bin',n,mold=0)
   if (.not. c_associated(mapping%cptr())) error stop 'Could not create mapping'
   call c_f_pointer(mapping%cptr(),values,[int(n)])
   values = [(i*i,i=1,int(n))]
   call mapping%destroy()
   nullify(values)
   call mapping%create(FMMAP_OLD,'mapped-array.bin',n,mold=0)
   if (.not. c_associated(mapping%cptr())) error stop 'Could not reopen mapping'
   call c_f_pointer(mapping%cptr(),values,[int(n)])
   if (any(values /= [(i*i,i=1,int(n))])) error stop 'Persisted values differ'
   print '(a,8i5)', 'Squares read back from mapped file:',values
   call mapping%destroy()
   nullify(values)
   open(newunit=unit,file='mapped-array.bin',status='old')
   close(unit,status='delete')
   print '(a)', 'PASS fmmap'
end program
