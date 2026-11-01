! Independent MIT API consumer; see licenses/data-ten-drivers-MIT.txt.
program rearray_reference
   use, intrinsic :: iso_fortran_env, only: real64
   use rearrayfx, only: rearray_real64_r2
   implicit none
   real, parameter :: factors(*)=[1.0,1.5,2.0,3.0]
   integer, parameter :: columns(*)=[1,3,2,7,4,12,1,5]
   integer :: rows,factor,step,old,cols,i,j,overlap,entries,allocations
   real(real64) :: reference(4,12),assigned(2,3)
   entries=0; allocations=0
   do rows=1,4
      do factor=1,size(factors)
         block
            type(rearray_real64_r2) :: matrix
            matrix%overprov=factors(factor); old=0; reference=0
            do step=1,size(columns)
               cols=columns(step)
               call matrix%allocate([rows,cols]); allocations=allocations+1
               if (any(shape(matrix%view)/=[rows,cols])) error stop 'rearray view shape'
               overlap=min(old,cols)
               if (any(matrix%view(:,1:overlap)/=reference(1:rows,1:overlap))) &
                  error stop 'rearray active prefix preservation'
               entries=entries+rows*overlap
               do j=overlap+1,cols
                  do i=1,rows
                     reference(i,j)=real(1000*step+100*factor+10*j+i,real64)/8
                  end do
               end do
               matrix%view=reference(1:rows,1:cols)
               if (any(matrix%view/=reference(1:rows,1:cols))) error stop 'rearray written values'
               entries=entries+rows*cols; old=cols
            end do
            assigned=reshape([(real(i,real64)/7,i=1,6)],[2,3])
            matrix=assigned
            if (any(shape(matrix%view)/=[2,3])) error stop 'rearray assignment shape'
            if (any(matrix%view/=assigned)) error stop 'rearray assignment values'
            entries=entries+6
         end block
      end do
   end do
   if (allocations/=128) error stop 'rearray allocation count'
   print '(a,i0)', '16 growth/shrink traces; 128 explicit allocations; scalar references: ',entries
   print '(a)', 'Four row counts and spare-capacity factors; active prefix preservation and shape-changing array assignment.'
   print '(a)', 'Inactive storage, zero-sized views, copying container objects and row-changing prefix semantics unverified.'
   print '(a)', 'PASS rearray-growth-reference'
end program
