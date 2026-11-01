! Independent MIT-licensed driver; see licenses/tangents-blocks-drivers-MIT.txt.
module sparse_block_fixture
   use dbcsr_api
   use, intrinsic :: iso_fortran_env, only: real64
   implicit none
   type :: matrix_handle
      type(dbcsr_type) :: matrix
      type(dbcsr_distribution_type) :: distribution
      integer, pointer :: row_sizes(:)=>null(),col_sizes(:)=>null(),rows(:)=>null(),cols(:)=>null()
   end type
contains
   subroutine make_matrix(handle,row_parts,col_parts,dense)
      type(matrix_handle), intent(out) :: handle
      integer, intent(in) :: row_parts(:),col_parts(:)
      real(real64), intent(in) :: dense(:,:)
      integer :: i,j,r,s,nr,nc
      allocate(handle%row_sizes(size(row_parts)),handle%col_sizes(size(col_parts)))
      allocate(handle%rows(size(row_parts)),handle%cols(size(col_parts)))
      handle%row_sizes=row_parts; handle%col_sizes=col_parts; handle%rows=0; handle%cols=0
      call dbcsr_distribution_new(handle%distribution,group=0,row_dist=handle%rows,col_dist=handle%cols)
      call dbcsr_create(handle%matrix,'fixture',handle%distribution,dbcsr_type_no_symmetry, &
         handle%row_sizes,handle%col_sizes,data_type=dbcsr_type_real_8)
      s=1
      do j=1,size(col_parts)
         nc=col_parts(j); r=1
         do i=1,size(row_parts)
            nr=row_parts(i)
            if (any(dense(r:r+nr-1,s:s+nc-1)/=0)) &
               call dbcsr_put_block(handle%matrix,i,j,dense(r:r+nr-1,s:s+nc-1))
            r=r+nr
         end do
         s=s+nc
      end do
      call dbcsr_finalize(handle%matrix)
   end subroutine
   subroutine unpack(handle,dense)
      type(matrix_handle), intent(inout) :: handle
      real(real64), intent(out) :: dense(:,:)
      real(real64), pointer :: block(:,:)
      logical :: transposed,found
      integer :: i,j,r,s,nr,nc
      dense=0; s=1
      do j=1,size(handle%col_sizes)
         nc=handle%col_sizes(j); r=1
         do i=1,size(handle%row_sizes)
            nr=handle%row_sizes(i)
            call dbcsr_get_block_p(handle%matrix,i,j,block,transposed,found)
            if (found) then
               if (transposed) then
                  dense(r:r+nr-1,s:s+nc-1)=transpose(block)
               else
                  dense(r:r+nr-1,s:s+nc-1)=block
               end if
            end if
            r=r+nr
         end do
         s=s+nc
      end do
   end subroutine
   subroutine release_matrix(handle)
      type(matrix_handle), intent(inout) :: handle
      call dbcsr_release(handle%matrix)
      call dbcsr_distribution_release(handle%distribution)
      deallocate(handle%row_sizes,handle%col_sizes,handle%rows,handle%cols)
   end subroutine
end module

program reference_block_products
   use sparse_block_fixture
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   real(real64), parameter :: alphas(*)=[1.0_real64,-1.25_real64,0.0_real64,2.0_real64,0.0_real64,0.5_real64]
   real(real64), parameter :: betas(*)=[0.0_real64,0.5_real64,-1.0_real64,0.0_real64,0.0_real64,1.0_real64]
   character, parameter :: flags(2)=['N','T']
   type(matrix_handle) :: ah,bh,ch
   integer, allocatable :: mp(:),kp(:),np(:),row_block(:),col_block(:)
   real(real64), allocatable :: a(:,:),b(:,:),c(:,:),result(:,:)
   real(real64) :: da,db,dc,expected,scale,error,max_error
   integer :: shape,pattern,ta,tb,pair,m,k,n,i,j,h,runs,entries
   runs=0; entries=0; max_error=0
   call dbcsr_init_lib(0)
   do shape=1,3
      select case(shape)
      case(1)
         mp=[1,2,1]; kp=[2,1]; np=[1,3]
      case(2)
         mp=[2,1]; kp=[1,3,2]; np=[2,1,2]
      case(3)
         mp=[1,1]; kp=[1,2]; np=[2,1]
      end select
      m=sum(mp); k=sum(kp); n=sum(np)
      allocate(a(m,k),b(k,n),c(m,n),result(m,n))
      do pattern=1,4
         da=8; db=8; dc=8
         if (pattern==3) then
            da=7; db=11; dc=13
         end if
         do j=1,k
            do i=1,m
               a(i,j)=real(2*i-3*j+1,real64)/da
            end do
         end do
         do j=1,n
            do i=1,k
               b(i,j)=real(3*i+j-2,real64)/db
            end do
            do i=1,m
               c(i,j)=real(i-2*j+3,real64)/dc
            end do
         end do
         if (pattern==2) then
            row_block=block_indices(mp); col_block=block_indices(kp)
            do j=1,k
               do i=1,m
                  if (modulo(row_block(i)+col_block(j),2)/=0) a(i,j)=0
               end do
            end do
            row_block=block_indices(kp); col_block=block_indices(np)
            do j=1,n
               do i=1,k
                  if (modulo(2*row_block(i)+col_block(j),3)==0) b(i,j)=0
               end do
            end do
         else if (pattern==4) then
            a=0
         end if
         do ta=1,2
            do tb=1,2
               do pair=1,size(alphas)
                  if (ta==1) then
                     call make_matrix(ah,mp,kp,a)
                  else
                     call make_matrix(ah,kp,mp,transpose(a))
                  end if
                  if (tb==1) then
                     call make_matrix(bh,kp,np,b)
                  else
                     call make_matrix(bh,np,kp,transpose(b))
                  end if
                  call make_matrix(ch,mp,np,c)
                  call dbcsr_multiply(flags(ta),flags(tb),alphas(pair),ah%matrix,bh%matrix, &
                     betas(pair),ch%matrix,filter_eps=0.0_real64)
                  call unpack(ch,result)
                  if (.not.all(ieee_is_finite(result))) error stop 'nonfinite sparse product'
                  do j=1,n
                     do i=1,m
                        expected=betas(pair)*c(i,j); scale=1+abs(expected)
                        do h=1,k
                           expected=expected+alphas(pair)*a(i,h)*b(h,j)
                           scale=scale+abs(alphas(pair)*a(i,h)*b(h,j))
                        end do
                        error=abs(result(i,j)-expected)/scale
                        if (error>128*epsilon(error)*(k+2)) error stop 'scalar-loop product reference differs'
                        max_error=max(max_error,error); entries=entries+1
                     end do
                  end do
                  call release_matrix(ah); call release_matrix(bh); call release_matrix(ch)
                  runs=runs+1
               end do
            end do
         end do
      end do
      deallocate(a,b,c,result)
   end do
   call dbcsr_finalize_lib()
   print '(a,i0,a,i0)', 'Block-sparse products: ',runs,'; scalar reference entries: ',entries
   print '(a,es14.5)', 'Maximum normalized product error: ',max_error
   print '(a)', 'All N/T flag pairs, irregular blocks, sparse/empty inputs and alpha/beta accumulation checked.'
   print '(a)', 'Serial real64 CPU build only; MPI, accelerators and symmetry storage unverified.'
   print '(a)', 'PASS dbcsr-products-reference'
contains
   function block_indices(parts) result(indices)
      integer, intent(in) :: parts(:)
      integer :: indices(sum(parts)),i,j,pos
      pos=0
      do i=1,size(parts)
         do j=1,parts(i)
            pos=pos+1; indices(pos)=i
         end do
      end do
   end function
end program
