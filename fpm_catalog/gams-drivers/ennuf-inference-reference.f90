! Independent MIT-licensed driver; see licenses/inference-pairs-drivers-MIT.txt.
program reference_ennuf_pipelines
   use neural_net_mod, only: dense,activation_function
   use ennuf_example_mod, only: ennuf_example
   use, intrinsic :: iso_fortran_env, only: real32,real64
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, parameter :: channel_counts(*)=[1,2,5]
   character(len=10), parameter :: names(*)=[character(len=10) :: 'relu','leakyrelu','sigmoid','tanh','softmax']
   real(real32), parameter :: grid(*)=[-2.0_real32,-1.0_real32,-0.5_real32,-0.25_real32,0.0_real32, &
      0.25_real32,0.5_real32,1.0_real32,2.0_real32]
   integer, allocatable :: nodes(:)
   integer :: architecture,ch,channels,act,bias_mode,pattern,sample,l,i,j,c,pipelines,entries,final_entries,dense_calls
   integer :: wrapper_calls,regions(4),region,ix,iy
   real(real64) :: z,error,max_error,softmax_error,max_softmax,expected,h1,h2,wrapper_error,max_wrapper
   real(real32) :: wrapper_input(1,2),wrapper_output(1,1)
   pipelines=0; entries=0; final_entries=0; dense_calls=0; max_error=0; max_softmax=0; max_wrapper=0
   do architecture=1,4
      call set_architecture(architecture)
      do ch=1,size(channel_counts)
         channels=channel_counts(ch)
         do act=1,size(names)
            do bias_mode=0,1
               do pattern=1,2
                  do sample=1,11
                     block
                        real(real32), allocatable :: current(:,:),weighted(:,:),activated(:,:),w(:,:),b(:)
                        real(real64), allocatable :: previous(:,:),next(:,:),raw(:)
                        allocate(current(channels,nodes(0))); current=0
                        if (sample>=2 .and. sample<=nodes(0)+1) then
                           do c=1,channels
                              current(c,sample-1)=real(c,real32)/real(channels+1,real32)
                           end do
                        else if (sample>nodes(0)+1) then
                           do j=1,nodes(0)
                              do c=1,channels
                                 current(c,j)=real(modulo(sample*(2*j+1)+3*c,17)-8,real32)/8
                              end do
                           end do
                        end if
                        previous=real(current,real64)
                        do l=1,ubound(nodes,1)
                           allocate(w(nodes(l),nodes(l-1)),b(nodes(l)),weighted(channels,nodes(l)))
                           allocate(activated(channels,nodes(l)),next(channels,nodes(l)),raw(nodes(l)))
                           do i=1,nodes(l)
                              b(i)=real(i-2*l,real32)/8
                              if (pattern==2) b(i)=real(i-2*l,real32)/9
                              do j=1,nodes(l-1)
                                 w(i,j)=real(2*i-3*j+l,real32)/8
                                 if (pattern==2) w(i,j)=real(2*i-3*j+l,real32)/7
                              end do
                           end do
                           if (bias_mode==1) then
                              call dense(current,weighted,channels,nodes(l-1),nodes(l),w,b)
                           else
                              call dense(current,weighted,channels,nodes(l-1),nodes(l),w)
                           end if
                           if (act==2) then
                              call activation_function(weighted,activated,channels,nodes(l),names(act),alpha=0.125_real32)
                           else
                              call activation_function(weighted,activated,channels,nodes(l),names(act))
                           end if
                           if (.not.all(ieee_is_finite(activated))) error stop 'nonfinite ennuf layer output'
                           do c=1,channels
                              do i=1,nodes(l)
                                 z=0
                                 if (bias_mode==1) z=real(b(i),real64)
                                 do j=1,nodes(l-1)
                                    z=z+real(w(i,j),real64)*previous(c,j)
                                 end do
                                 raw(i)=z
                              end do
                              if (act==5) then
                                 raw=exp(raw-maxval(raw)); next(c,:)=raw/sum(raw)
                                 softmax_error=abs(sum(real(activated(c,:),real64))-1)
                                 if (any(activated(c,:)<=0) .or. softmax_error>2e-6_real64) &
                                    error stop 'softmax row normalization differs'
                                 max_softmax=max(max_softmax,softmax_error)
                              else
                                 do i=1,nodes(l)
                                    next(c,i)=activate(raw(i),act)
                                 end do
                              end if
                              do i=1,nodes(l)
                                 error=abs(real(activated(c,i),real64)-next(c,i))/(1+abs(next(c,i)))
                                 if (error>5e-6_real64) error stop 'ennuf scalar pipeline reference differs'
                                 max_error=max(max_error,error); entries=entries+1
                              end do
                           end do
                           current=activated; previous=next; dense_calls=dense_calls+1
                           deallocate(w,b,weighted,activated,next,raw)
                        end do
                        final_entries=final_entries+channels*nodes(ubound(nodes,1)); pipelines=pipelines+1
                     end block
                  end do
               end do
            end do
         end do
      end do
      deallocate(nodes)
   end do
   wrapper_calls=0; regions=0
   do ix=1,size(grid)
      do iy=1,size(grid)
         wrapper_input(1,:)=[grid(ix),grid(iy)]
         call ennuf_example(wrapper_input,wrapper_output)
         if (.not.all(ieee_is_finite(wrapper_output))) error stop 'nonfinite generated-model output'
         h1=real(grid(ix),real64)+2*real(grid(iy),real64)+0.5_real64
         h2=-real(grid(ix),real64)+0.5_real64*real(grid(iy),real64)-0.25_real64
         expected=2*max(h1,0.0_real64)-3*max(h2,0.0_real64)+1
         wrapper_error=abs(real(wrapper_output(1,1),real64)-expected)/(1+abs(expected))
         if (wrapper_error>5e-6_real64) error stop 'generated ennuf model closed-form reference differs'
         region=1+merge(1,0,h1>0)+2*merge(1,0,h2>0); regions(region)=regions(region)+1
         max_wrapper=max(max_wrapper,wrapper_error); wrapper_calls=wrapper_calls+1
      end do
   end do
   if (any(regions==0)) error stop 'not every generated-model ReLU region is covered'
   print '(a,i0,a,i0)', 'Ennuf pipeline batches: ',pipelines,'; dense and activation calls each: ',dense_calls
   print '(a,i0,a,i0)', 'All-stage reference entries: ',entries,'; final-layer entries included: ',final_entries
   print '(a,i0,a,4i6)', 'Generated-model evaluations: ',wrapper_calls,'; four ReLU-region counts: ',regions
   print '(a,3es14.5)', 'Max normalized pipeline error, softmax sum error and generated-model error: ', &
      max_error,max_softmax,max_wrapper
   print '(a)', 'Fixed REAL32 inference only; conversion, convolution, training and extreme softmax logits unverified.'
   print '(a)', 'PASS ennuf-inference-reference'
contains
   subroutine set_architecture(which)
      integer, intent(in) :: which
      if (which<=3) then
         allocate(nodes(0:2))
      else
         allocate(nodes(0:3))
      end if
      select case(which)
      case(1)
         nodes=[1,2,1]
      case(2)
         nodes=[2,3,2]
      case(3)
         nodes=[3,2,1]
      case(4)
         nodes=[2,4,3,2]
      end select
   end subroutine
   real(real64) function activate(x,which) result(value)
      real(real64), intent(in) :: x
      integer, intent(in) :: which
      select case(which)
      case(1)
         value=max(0.0_real64,x)
      case(2)
         value=merge(x,0.125_real64*x,x>=0)
      case(3)
         if (x>=0) then
            value=1/(1+exp(-x))
         else
            value=exp(x)/(1+exp(x))
         end if
      case(4)
         value=2/(1+exp(-2*x))-1
      end select
   end function
end program
