! Independent MIT-licensed driver; see licenses/projection-training-drivers-MIT.txt.
program reference_affine_training
   use nf, only: network,input,dense,linear,sgd
   use, intrinsic :: iso_fortran_env, only: real64
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, parameter :: seeds(3)=[42,1729,314159]
   integer :: n,map,sd,batch_mode,batch,nsamples,nseed,i,j,k,idx,runs,entries
   integer, allocatable :: seed(:)
   real, allocatable :: samples(:,:),targets(:,:),point(:)
   real :: prediction(2)
   real(real64) :: w(2,2),bias(2),expected(2),initial_mse,final_mse,err,max_err,max_mse,max_ratio
   runs=0; entries=0; max_err=0; max_mse=0; max_ratio=0
   call random_seed(size=nseed)
   allocate(seed(nseed))
   do n=1,2
      nsamples=3**n
      allocate(samples(n,nsamples),targets(2,nsamples),point(n))
      do i=1,nsamples
         idx=i-1
         do j=1,n
            samples(j,i)=real(mod(idx,3)-1)
            idx=idx/3
         end do
      end do
      do map=1,2
         w(1,:)=[0.75_real64,-0.5_real64]*real(map,real64)
         w(2,:)=[-0.25_real64,1.0_real64]/real(map,real64)
         bias=[0.5_real64,-0.75_real64]*real(map,real64)
         do i=1,nsamples
            targets(:,i)=real(reference(real(samples(:,i),real64)))
         end do
         do sd=1,size(seeds)
            do batch_mode=1,2
               block
                  type(network) :: net
                  seed=[(seeds(sd)+37*i,i=1,nseed)]
                  call random_seed(put=seed)
                  net=network([input(n),dense(2,activation=linear())])
                  initial_mse=training_mse(net)
                  batch=1
                  if (batch_mode==2) batch=nsamples
                  call net%train(samples,targets,batch_size=batch,epochs=400,optimizer=sgd(learning_rate=0.1))
                  final_mse=training_mse(net)
                  if (.not.ieee_is_finite(final_mse)) error stop 'nonfinite training loss'
                  if (final_mse>1e-8_real64 .or. final_mse>1e-5_real64*initial_mse) &
                     error stop 'training loss did not approach the known zero minimum'
                  ! Test 11-point Cartesian grids, including points absent from training.
                  do i=0,10
                     point(1)=real(i-5)/5
                     do k=0,merge(0,10,n==1)
                        if (n==2) point(2)=real(k-5)/5
                        prediction=net%predict(point)
                        expected=reference(real(point,real64))
                        if (.not.all(ieee_is_finite(prediction))) error stop 'nonfinite held-out prediction'
                        err=maxval(abs(real(prediction,real64)-expected))/(1+maxval(abs(expected)))
                        if (err>2e-4_real64) error stop 'independent affine prediction differs'
                        max_err=max(max_err,err); entries=entries+2
                     end do
                  end do
                  max_mse=max(max_mse,final_mse); max_ratio=max(max_ratio,final_mse/initial_mse)
                  runs=runs+1
               end block
            end do
         end do
      end do
      deallocate(samples,targets,point)
   end do
   print '(a,i0,a,i0)', 'Affine training runs: ',runs,'; test prediction entries: ',entries
   print '(a,3es14.5)', 'Max normalized prediction error, final MSE, final/initial MSE: ',max_err,max_mse,max_ratio
   print '(a)', 'PASS neural-affine-reference'
contains
   function reference(x) result(y)
      real(real64), intent(in) :: x(:)
      real(real64) :: y(2)
      integer :: a,b
      y=bias
      do a=1,2
         do b=1,size(x)
            y(a)=y(a)+w(a,b)*x(b)
         end do
      end do
   end function
   function training_mse(net) result(mse)
      type(network), intent(in out) :: net
      real(real64) :: mse,r(2)
      integer :: a
      mse=0
      do a=1,nsamples
         r=real(net%predict(samples(:,a)),real64)-reference(real(samples(:,a),real64))
         if (.not.all(ieee_is_finite(r))) error stop 'nonfinite training prediction'
         mse=mse+sum(r*r)
      end do
      mse=mse/real(2*nsamples,real64)
   end function
end program
