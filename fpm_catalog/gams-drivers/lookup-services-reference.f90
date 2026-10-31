! Independent API consumer; MIT: licenses/lookup-fastmath-drivers-MIT.txt.
program lookup_services_reference
   use, intrinsic :: iso_fortran_env, only: dp => real64
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   use m_lookup_table, only: LT_t, LT_loc_t, LT_create, LT_set_col, LT_set_col_data, LT_add_col, &
      LT_get_loc, LT_get_col, LT_get_mcol, LT_get_col_at_loc, LT_get_mcol_at_loc
   implicit none
   type(LT_t) :: table,original
   real(dp), parameter :: source_x(*) = [-2._dp,-1.25_dp,.25_dp,1._dp,2._dp]
   real(dp) :: grid(9),source_y(5),stored(9,3),baseline(9,3),q,max_error
   integer :: i,queries
   grid = [(-2._dp+.5_dp*i,i=0,8)]
   source_y = (source_x+1)**2
   table = LT_create(-2._dp,2._dp,n_points=9,n_cols=2)
   if (maxval(abs(table%x-grid)) > 1.e-14_dp) error stop 'linear grid creation'
   call LT_set_col_data(table,1,2*grid+1)
   call LT_set_col(table,2,source_x,source_y)
   call LT_add_col(table,source_x,[(7._dp,i=1,5)])
   if (table%n_cols /= 3 .or. table%n_points /= 9) error stop 'added column dimensions'
   stored(:,1) = 2*grid+1
   do i = 1,9
      stored(i,2) = reference(source_x,source_y,grid(i))
   end do
   stored(:,3) = 7._dp
   baseline = stored
   original = table
   call LT_set_col_data(table,1,[(3._dp,i=1,9)],add=.true.)
   call LT_set_col(table,2,source_x,[(-.5_dp,i=1,5)],add=.true.)
   stored(:,1) = stored(:,1)+3
   stored(:,2) = stored(:,2)-.5_dp
   queries = 0
   max_error = 0._dp
   do i = 0,48
      q = -3._dp+real(i,dp)/8
      call check(table,stored,q)
      call check(original,baseline,q)
   end do
   if (queries /= 98) error stop 'lookup query count'
   print '(a)', '98 queries: updated and independent copied tables, 3 columns, 4 lookup routes.'
   print '(a,es12.4)', 'Maximum error versus independent two-stage interpolation: ',max_error
   print '(a)', 'Location coordinates, endpoints, clamping, resampling, column addition and updates checked.'
   print '(a)', 'PASS lookup-services-reference'
contains
   real(dp) function reference(x,y,query) result(value)
      real(dp), intent(in) :: x(:),y(:),query
      integer :: j
      real(dp) :: fraction
      value = y(1)
      if (query <= x(1)) return
      value = y(size(y))
      if (query >= x(size(x))) return
      do j = 2,size(x)
         if (query <= x(j)) then
            fraction = (query-x(j-1))/(x(j)-x(j-1))
            value = y(j-1)+fraction*(y(j)-y(j-1))
            return
         end if
      end do
   end function reference
   subroutine check(t,values,query)
      type(LT_t), intent(in) :: t
      real(dp), intent(in) :: values(9,3),query
      type(LT_loc_t) :: loc
      real(dp) :: expected(3),direct(3),located(3),answers(4),coordinate
      integer :: c
      loc = LT_get_loc(t,query)
      if (loc%low_ix < 1 .or. loc%low_ix > 8) error stop 'location index bounds'
      if (.not. ieee_is_finite(loc%low_frac)) error stop 'nonfinite location fraction'
      if (loc%low_frac < 0 .or. loc%low_frac > 1) error stop 'clamped location fraction'
      coordinate = loc%low_frac*grid(loc%low_ix)+(1-loc%low_frac)*grid(loc%low_ix+1)
      if (abs(coordinate-max(-2._dp,min(2._dp,query))) > 1.e-12_dp) error stop 'location coordinate'
      direct = LT_get_mcol(t,query)
      located = LT_get_mcol_at_loc(t,loc)
      do c = 1,3
         expected(c) = reference(grid,values(:,c),query)
         answers = [direct(c),located(c),LT_get_col(t,c,query),LT_get_col_at_loc(t,c,loc)]
         if (.not. all(ieee_is_finite(answers))) error stop 'nonfinite lookup'
         max_error = max(max_error,maxval(abs(answers-expected(c))))
         if (maxval(abs(answers-expected(c))) > 2.e-12_dp) error stop 'independent lookup reference'
      end do
      queries = queries+1
   end subroutine check
end program lookup_services_reference
