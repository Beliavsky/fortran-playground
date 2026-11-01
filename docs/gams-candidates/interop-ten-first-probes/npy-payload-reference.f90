! Independent MIT consumer; see licenses/interop-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: int32,real64
   use m_npy, only: save_npy
   implicit none
   real(real64), allocatable :: matrix(:,:),payload(:,:)
   character(:), allocatable :: header
   character(8) :: magic
   character(40) :: shape
   integer(int32) :: length
   integer :: rows,cols,i,j,unit,bytes,checks,p
   checks=0
   do rows=1,5
      do cols=1,7
         allocate(matrix(rows,cols),payload(rows,cols))
         do j=1,cols
            do i=1,rows
               matrix(i,j)=real(19*i-7*j,real64)/8
            end do
         end do
         call save_npy('fixture.npy',matrix)
         open(newunit=unit,file='fixture.npy',status='old',access='stream',form='unformatted')
         read(unit) magic,length
         if (magic/=achar(147)//'NUMPY'//achar(2)//achar(0)) error stop 'NPY version/magic'
         if (length<1 .or. length>4096) error stop 'Header length'
         allocate(character(length)::header)
         read(unit) header
         if (index(header,"'<f8'")==0 .or. index(header,'True')==0) error stop 'dtype/order'
         ! Ignore whitespace only when checking the exact expected shape text.
         do
            p=index(header,' ')
            if(p==0) exit
            header=header(:p-1)//header(p+1:)
         end do
         write(shape,'(a,i0,a,i0,a)') "'shape':(",rows,',',cols,')'
         if (index(header,trim(shape))==0) error stop 'Shape header'
         read(unit) payload
         inquire(unit=unit,size=bytes)
         if (bytes/=12+length+8*rows*cols) error stop 'NPY byte length'
         do j=1,cols
            do i=1,rows
               if(payload(i,j)/=real(19*i-7*j,real64)/8) error stop 'Raw payload'
               checks=checks+1
            end do
         end do
         close(unit,status='delete')
         deallocate(matrix,payload,header)
      end do
   end do
   print '(a,i0)', '35 NPY headers and independently read REAL64 payload values: ',checks
   print '(a)', 'PASS npy-payload-reference'
end program
