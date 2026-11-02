! Independent MIT consumer; see licenses/statistics-rank-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64, int64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_linalg_constants, only: ilp
   use stdlib_stats, only: var
   implicit none
   real(real64),parameter :: reference(3,64)=reshape([ &
      0.5615234375_real64, 0.4755859375_real64, 0.3818359375_real64, 0.347222222222222222_real64, &
      0.0694444444444444444_real64, 0.277777777777777778_real64, 0.5615234375_real64, 0.724609375_real64, &
      0.91796875_real64, 0.56640625_real64, 0.33203125_real64, 1.42578125_real64, 0.810546875_real64, &
      0.5888671875_real64, 0.9755859375_real64, 1.05902777777777778_real64, 0.673611111111111111_real64, &
      0.597222222222222222_real64, 0.6279296875_real64, 0.5888671875_real64, 0.498046875_real64, &
      0.347222222222222222_real64, 0.0694444444444444444_real64, 0.277777777777777778_real64, 0.51875_real64, &
      0.405_real64, 0.32125_real64, 0.347222222222222222_real64, 0.0694444444444444444_real64, &
      0.277777777777777778_real64, 0.51875_real64, 0.6175_real64, 0.875_real64, 0.600694444444444444_real64, &
      0.548611111111111111_real64, 1.26736111111111111_real64, 0.7525_real64, 0.7975_real64, 1.03375_real64, &
      0.9208984375_real64, 0.9140625_real64, 0.9755859375_real64, 0.73125_real64, 0.56375_real64, 0.40625_real64, &
      0.347222222222222222_real64, 0.0694444444444444444_real64, 0.277777777777777778_real64, &
      0.457465277777777778_real64, 0.357638888888888889_real64, 0.342881944444444444_real64, 0.279296875_real64, &
      0.146484375_real64, 0.3818359375_real64, 0.457465277777777778_real64, 0.542100694444444444_real64, &
      1.10460069444444444_real64, 0.4765625_real64, 0.5_real64, 1.42578125_real64, 0.627170138888888889_real64, &
      0.934895833333333333_real64, 0.870659722222222222_real64, 0.9208984375_real64, 0.9140625_real64, &
      0.9755859375_real64, 0.634548611111111111_real64, 0.849392361111111111_real64, 0.453559027777777778_real64, &
      0.2958984375_real64, 0.7216796875_real64, 0.498046875_real64, 0.537627551020408163_real64, &
      0.420918367346938776_real64, 0.392219387755102041_real64, 0.43375_real64, 0.2325_real64, 0.4075_real64, &
      0.537627551020408163_real64, 0.605229591836734694_real64, 0.969387755102040816_real64, 0.4765625_real64, &
      0.5_real64, 1.42578125_real64, 0.656887755102040816_real64, 0.947704081632653061_real64, &
      0.94961734693877551_real64, 0.8925_real64, 0.8525_real64, 0.95375_real64, 0.667729591836734694_real64, &
      0.73788265306122449_real64, 0.554846938775510204_real64, 0.43375_real64, 0.58875_real64, 0.55625_real64, &
      0.4794921875_real64, 0.479248046875_real64, 0.511474609375_real64, 0.43375_real64, 0.2325_real64, 0.4075_real64, &
      0.4794921875_real64, 0.761474609375_real64, 0.903076171875_real64, 0.39125_real64, 0.5625_real64, 1.20875_real64, &
      0.574951171875_real64, 1.00537109375_real64, 0.882568359375_real64, 0.745225694444444444_real64, &
      0.852430555555555556_real64, 0.862847222222222222_real64, 0.595703125_real64, 0.742919921875_real64, &
      0.67138671875_real64, 0.43375_real64, 0.58875_real64, 0.55625_real64, 0.444058641975308642_real64, &
      0.516589506172839506_real64, 0.599151234567901235_real64, 0.388020833333333333_real64, 0.387152777777777778_real64, &
      0.525173611111111111_real64, 0.444058641975308642_real64, 0.706790123456790123_real64, 0.847608024691358025_real64, &
      0.349826388888888889_real64, 0.472222222222222222_real64, 1.05251736111111111_real64, 0.542438271604938272_real64, &
      1.02507716049382716_real64, 0.819058641975308642_real64, 0.745225694444444444_real64, 0.852430555555555556_real64, &
      0.862847222222222222_real64, 0.588348765432098765_real64, 0.867283950617283951_real64, 0.820216049382716049_real64, &
      0.439670138888888889_real64, 0.882378472222222222_real64, 0.924045138888888889_real64, 0.4534375_real64, &
      0.50890625_real64, 0.5734375_real64, 0.417729591836734694_real64, 0.422193877551020408_real64, &
      0.502551020408163265_real64, 0.4534375_real64, 0.72140625_real64, 0.84328125_real64, 0.349826388888888889_real64, &
      0.472222222222222222_real64, 1.05251736111111111_real64, 0.6128125_real64, 1.094375_real64, 0.7634375_real64, &
      0.813137755102040816_real64, 0.846301020408163265_real64, 0.752551020408163265_real64, 0.61015625_real64, &
      0.825_real64, 0.89015625_real64, 0.493622448979591837_real64, 0.827806122448979592_real64, &
      1.06441326530612245_real64, 0.454803719008264463_real64, 0.586518595041322314_real64, 0.574121900826446281_real64, &
      0.417729591836734694_real64, 0.422193877551020408_real64, 0.502551020408163265_real64, 0.454803719008264463_real64, &
      0.748966942148760331_real64, 0.834710743801652893_real64, 0.351403061224489796_real64, 0.599489795918367347_real64, &
      1.05548469387755102_real64, 0.573347107438016529_real64, 1.03589876033057851_real64, 0.829287190082644628_real64, &
      0.725341796875_real64, 0.814453125_real64, 0.8896484375_real64, 0.568956611570247934_real64, &
      0.842975206611570248_real64, 0.82618801652892562_real64, 0.493622448979591837_real64, 0.827806122448979592_real64, &
      1.06441326530612245_real64 ],[3,64])

   complex(real64),allocatable :: x(:,:),saved(:,:)
   logical,allocatable :: mask(:,:)
   integer :: n,k,mode,i,j,index,selected
   real(real64) :: result(3),expected(3),factor
   integer :: correction
   index=0
   do n=4,11
      allocate(x(n,3),mask(n,3))
      do k=1,4
         do j=1,3
            do i=1,n
               x(i,j)=cmplx(real(mod(i*i+3*j*i+2*k*j,17)-8,real64)/8, &
                  real(mod(2*i*i+j*i+k*(j+1),19)-9,real64)/8,real64)
            end do
         end do
         saved=x
         do mode=0,1
            index=index+1
            do i=1,n
               mask(i,:)=mode==0.or.mod(i+k,3)/=0
            end do
            selected=count(mask(:,1))

            do correction=0,1
               factor=real(selected,real64)/real(selected-correction,real64)
               expected=reference(:,index)*factor
               result=var(x,dim=1,mask=mask,corrected=correction==1)
               do j=1,3
                  call check(result(j),expected(j))
                  call check(var(x(:,j),mask=mask(:,j),corrected=correction==1),expected(j))
               end do
               result=var(transpose(x),dim=2,mask=transpose(mask),corrected=correction==1)
               do j=1,3
                  call check(result(j),expected(j))
               end do
            end do

            if(any(x/=saved)) error stop 'Statistics input preservation'
         end do
      end do
      deallocate(x,mask)
   end do
   print '(a,i0)', 'Independent exact-reference complex data selections: ',index
   print '(a)', 'PASS stdlib-complex-variances-reference'
contains
   subroutine check(actual,expected)
      real(real64),intent(in) :: actual,expected
      if(.not.ieee_is_finite(actual)) error stop 'Nonfinite result'
      if(abs(actual-expected)>2.e-10_real64*max(1._real64,abs(expected))) error stop 'Independent reference'
   end subroutine
   subroutine checkz(actual,expected)
      complex(real64),intent(in) :: actual,expected
      call check(real(actual,real64),real(expected,real64))
      call check(aimag(actual),aimag(expected))
   end subroutine
   subroutine check_matrix(actual,expected)
      complex(real64),intent(in) :: actual(:,:),expected(:,:)
      integer :: i,j
      if(any(shape(actual)/=shape(expected))) error stop 'Matrix shape'
      do j=1,size(actual,2)
         do i=1,size(actual,1)
            call checkz(actual(i,j),expected(i,j))
         end do
      end do
   end subroutine
   function identity(n) result(a)
      integer,intent(in) :: n
      complex(real64) :: a(n,n)
      integer :: i
      a=0
      do i=1,n
         a(i,i)=1
      end do
   end function
   function unitary(n,k) result(q)
      integer,intent(in) :: n,k
      complex(real64) :: q(n,n),v(n)
      real(real64) :: denominator
      integer :: i,j
      do i=1,n
         v(i)=cmplx(real(i,real64),real(mod(i+k,4)-2,real64),real64)
      end do
      denominator=real(dot_product(v,v),real64)
      q=identity(n)
      do j=1,n
         do i=1,n
            q(i,j)=q(i,j)-2*v(i)*conjg(v(j))/denominator
         end do
      end do
      call check_matrix(matmul(conjg(transpose(q)),q),identity(n))
   end function
end program
