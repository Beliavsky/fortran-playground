! Independent API consumer; see licenses/sparse-spectra-drivers-MIT.txt.
program checked_symmetric_spectra
   use libscalapackfx_module
   use iso_fortran_env, only: dp=>real64
   use ieee_arithmetic, only: ieee_is_finite,ieee_value,ieee_quiet_nan
   implicit none
   integer, parameter :: sizes(4)=[2,3,5,8]
   real(dp), parameter :: scales(2)=[0.125_dp,4.0_dp],shifts(2)=[-2.0_dp,0.75_dp]
   type(blacsgrid) :: grid
   real(dp), allocatable :: a(:,:),vectors(:,:),original(:,:),q(:,:),eigenvalues(:),expected(:)
   real(dp) :: angle,c,s,temp,eigen_error,residual,orthogonality,value,norm_a
   real(dp) :: worst_eigen=0,worst_residual=0,worst_orthogonality=0
   integer :: desca(DLEN_),descz(DLEN_),rank,processes,info,n,shape_id,spectrum,basis,scale_id,shift_id
   integer :: triangle,blocksize,i,j,k,l,systems=0,entries=0
   character(1) :: uplo
   call blacsfx_pinfo(rank,processes)
   if (processes/=1) error stop 'one MPI process required'
   call grid%initgrid(1,1)
   do shape_id=1,4
      n=sizes(shape_id)
      allocate(original(n,n),q(n,n),eigenvalues(n),expected(n))
      do spectrum=1,3
         do basis=1,2
            q=0
            do i=1,n
               q(i,i)=1
            end do
            if (basis==2) then
               do l=1,2
                  do k=1,n-1
                     angle=0.17_dp*(k+2*l); c=cos(angle); s=sin(angle)
                     do i=1,n
                        temp=q(i,k)
                        q(i,k)=c*temp-s*q(i,k+1); q(i,k+1)=s*temp+c*q(i,k+1)
                     end do
                  end do
               end do
            end if
            do scale_id=1,2
               do shift_id=1,2
                  do i=1,n
                     select case(spectrum)
                     case(1)
                        expected(i)=real(i,dp)-real(n+1,dp)/2
                     case(2)
                        expected(i)=1+real(i*i,dp)/n
                     case(3)
                        expected(i)=real((i-1)/2-1,dp)
                     end select
                  end do
                  expected=scales(scale_id)*expected+shifts(shift_id)
                  original=0
                  do j=1,n
                     do i=1,n
                        do k=1,n
                           original(i,j)=original(i,j)+q(i,k)*expected(k)*q(j,k)
                        end do
                     end do
                  end do
                  norm_a=maxval(sum(abs(original),dim=2))
                  do triangle=1,2
                     uplo='L'
                     if (triangle==2) uplo='U'
                     do blocksize=1,2
                        call scalafx_creatematrix(grid,n,n,blocksize,blocksize,a,desca,info=info)
                        if (info/=0) error stop 'matrix descriptor'
                        call scalafx_creatematrix(grid,n,n,blocksize,blocksize,vectors,descz,info=info)
                        if (info/=0) error stop 'eigenvector descriptor'
                        if (any(shape(a)/=[n,n]).or.any(shape(vectors)/=[n,n])) error stop 'local matrix shape'
                        a=original
                        do j=1,n
                           do i=1,n
                              if ((triangle==1.and.i<j).or.(triangle==2.and.i>j)) &
                                 a(i,j)=ieee_value(0.0_dp,ieee_quiet_nan)
                           end do
                        end do
                        call scalafx_psyev(a,desca,eigenvalues,vectors,descz,jobz='V',uplo=uplo,info=info)
                        if (info/=0) error stop 'symmetric eigensolver status'
                        if (.not.all(ieee_is_finite(eigenvalues)).or..not.all(ieee_is_finite(vectors))) &
                           error stop 'nonfinite eigensystem'
                        eigen_error=maxval(abs(eigenvalues-expected))/(1+maxval(abs(expected)))
                        residual=0; orthogonality=0
                        do j=1,n
                           do i=1,n
                              value=-eigenvalues(j)*vectors(i,j)
                              do k=1,n
                                 value=value+original(i,k)*vectors(k,j)
                              end do
                              residual=max(residual,abs(value)/(1+norm_a))
                              value=0
                              if (i==j) value=-1
                              do k=1,n
                                 value=value+vectors(k,i)*vectors(k,j)
                              end do
                              orthogonality=max(orthogonality,abs(value))
                           end do
                        end do
                        worst_eigen=max(worst_eigen,eigen_error); worst_residual=max(worst_residual,residual)
                        worst_orthogonality=max(worst_orthogonality,orthogonality)
                        if (max(eigen_error,residual,orthogonality)>5e-12_dp) error stop 'independent spectral reference'
                        systems=systems+1; entries=entries+n
                        deallocate(a,vectors)
                     end do
                  end do
               end do
            end do
         end do
      end do
      deallocate(original,q,eigenvalues,expected)
   end do
   call grid%destruct()
   call blacsfx_exit(keepmpi=.false.)
   print '(a,i0)', 'Symmetric eigensystems: ',systems
   print '(a,i0)', 'Prescribed eigenvalue references: ',entries
   print '(a,es12.4)', 'Maximum normalized eigenvalue error: ',worst_eigen
   print '(a,es12.4)', 'Maximum normalized eigenpair residual: ',worst_residual
   print '(a,es12.4)', 'Maximum orthogonality residual: ',worst_orthogonality
   print '(a)', 'PASS scalapackfx-eigen-reference'
end program checked_symmetric_spectra
