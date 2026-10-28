module playground_psqp_functions
   use psqp_module, only: psqp_class,wp => psqp_wp
   implicit none
contains
    subroutine obj(me,nf,x,ff)

        !! user supplied subroutine (calculation of ff)

        class(psqp_class),intent(inout) :: me
        real(wp) :: ff
        integer  :: nf
        real(wp) :: x(nf)

        ff = x(1)**2 + x(2)**2 + x(3)  !objective function

    end subroutine obj

    subroutine dobj(me,nf,x,gf)

        !! user supplied subroutine (calculation of gf)

        class(psqp_class),intent(inout) :: me
        integer  :: nf
        real(wp) :: gf(nf),x(nf)

        gf(1) = 2.0_wp*x(1)
        gf(2) = 2.0_wp*x(2)
        gf(3) = 1.0_wp

    end subroutine dobj

    subroutine con(me,nf,kc,x,fc)

        !! user supplied subroutine (calculation of fc)

        class(psqp_class),intent(inout) :: me
        real(wp) :: fc
        integer  :: kc,nf
        real(wp) :: x(nf)

        select case (kc)
        case(1)
            fc = x(1)*x(2) - x(3)       !equality constraint (==0)
        case(2)
            fc = x(3) - 1.0_wp          !inequality constraint (>=0)
        case default
            error stop 'invalid kc'
        end select

    end subroutine con

    subroutine dcon(me,nf,kc,x,gc)

        !! user supplied subroutine (calculation of gc)

        class(psqp_class),intent(inout) :: me
        integer  :: kc,nf
        real(wp) :: gc(nf),x(nf)

        select case (kc)
        case(1)
            gc(1) = x(2)
            gc(2) = x(1)
            gc(3) = -1.0_wp
        case(2)
            gc(1) = 0.0_wp
            gc(2) = 0.0_wp
            gc(3) = 1.0_wp
        case default
            error stop 'invalid kc'
        end select

    end subroutine dcon

end module

! Minimize x1**2+x2**2+x3 with x1*x2=x3 and x3>=1.
! The minimum is 3 at (1,1,1) or (-1,-1,1).
program demo_psqp
   use playground_psqp_functions
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   type(psqp_class) :: solver
   real(wp) :: x(3),xl(3),xu(3),cf(3),cl(2),cu(2),rpar(5),f,cmax,gmax
   integer :: ix(3),ic(2),ipar(6),status
   x = [1.0_wp,2.0_wp,3.0_wp]
   xl = -10; xu = 10; ix = 3
   ic = [5,1]; cl = 0; cu = 0
   ipar = [500,1000,0,0,1,1]
   rpar = [0.0_wp,1e-10_wp,1e-10_wp,1e-8_wp,0.0_wp]
   call solver%psqpn(3,1,2,x,ix,xl,xu,cf,ic,cl,cu,ipar,rpar,f,cmax,gmax,0,status,obj,dobj,con,dcon)
   if (status<=0) error stop 'Optimization failed'
   if (.not. all(ieee_is_finite(x))) error stop 'Nonfinite optimum'
   if (.not. ieee_is_finite(f)) error stop 'Nonfinite objective'
   if (maxval(abs(abs(x)-1.0_wp))>1e-5_wp .or. x(3)<0) error stop 'Known optimum differs'
   if (abs(x(1)*x(2)-x(3))>1e-7_wp .or. x(3)<1.0_wp-1e-7_wp) error stop 'Constraint violated'
   if (abs(f-3.0_wp)>1e-6_wp) error stop 'Wrong objective'
   print '(a,3f14.8)', 'Optimal variables: ',x
   print '(a,f14.8)', 'Minimum objective: ',f
   print '(a,es12.3)', 'Maximum constraint violation: ',cmax
   print '(a,i0)', 'Termination code: ',status
   print '(a)', 'PASS psqp'
end program
