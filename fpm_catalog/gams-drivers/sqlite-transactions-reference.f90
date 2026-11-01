! Independent MIT API consumer; see licenses/state-ten-drivers-MIT.txt.
program sqlite_reference
   use sqliteff
   use iso_varying_string, only: varying_string
   implicit none
   type(SqliteDatabase_t) :: database
   type(SqliteStatement_t) :: statement
   type(varying_string) :: message,remaining
   integer :: i,rows,status
   call check(sqliteff_open(':memory:',database),SQLITE_OK)
   call execute('create table samples(k integer primary key, v real); begin;')
   call check(sqliteff_prepare(database,'insert into samples values(?,?);',statement,remaining),SQLITE_OK)
   do i=-32,31
      call check(sqliteff_bind_int(statement,1,i),SQLITE_OK)
      call check(sqliteff_bind_double(statement,2,dble(i)/8),SQLITE_OK)
      call check(sqliteff_step(statement),SQLITE_DONE)
      call check(sqliteff_reset(statement),SQLITE_OK)
   end do
   call check(sqliteff_finalize(statement),SQLITE_OK)
   call execute('commit; begin; update samples set v=v+100; insert into samples values(999,999); rollback;')
   call check(sqliteff_prepare(database,'select count(*),sum(v),avg(v),min(v),max(v) from samples;', &
      statement,remaining),SQLITE_OK)
   call check(sqliteff_step(statement),SQLITE_ROW)
   if (sqliteff_column_int(statement,0)/=64) error stop 'SQLite rollback row count'
   if (sqliteff_column_double(statement,1)/=-4.d0) error stop 'SQLite sum reference'
   if (sqliteff_column_double(statement,2)/=-0.0625d0) error stop 'SQLite average reference'
   if (sqliteff_column_double(statement,3)/=-4.d0) error stop 'SQLite minimum reference'
   if (sqliteff_column_double(statement,4)/=3.875d0) error stop 'SQLite maximum reference'
   call check(sqliteff_step(statement),SQLITE_DONE); call check(sqliteff_finalize(statement),SQLITE_OK)
   call execute('delete from samples where k%3=0;')
   call check(sqliteff_prepare(database,'select k,v from samples order by k;',statement,remaining),SQLITE_OK)
   rows=0
   do i=-32,31
      if (modulo(i,3)==0) cycle
      call check(sqliteff_step(statement),SQLITE_ROW)
      if (sqliteff_column_int(statement,0)/=i) error stop 'SQLite ordered key reference'
      if (sqliteff_column_double(statement,1)/=dble(i)/8) error stop 'SQLite ordered value reference'
      rows=rows+1
   end do
   if (rows/=43) error stop 'SQLite remaining rows'
   call check(sqliteff_step(statement),SQLITE_DONE); call check(sqliteff_finalize(statement),SQLITE_OK)
   call check(sqliteff_close(database),SQLITE_OK)
   print '(a)', '64 prepared/bound inserts; rollback restores five exact aggregates; 43 ordered rows after deletion.'
   print '(a)', 'In-memory database, commit/rollback, statement reset/finalize and independent integer/dyadic references.'
   print '(a)', 'Disk persistence, concurrent transactions, text/NULL values and database error recovery unverified.'
   print '(a)', 'PASS sqlite-transactions-reference'
contains
   subroutine check(actual,expected)
      integer, intent(in) :: actual,expected
      if (actual/=expected) error stop 'unexpected SQLite status'
   end subroutine
   subroutine execute(sql)
      character(*), intent(in) :: sql
      call check(sqliteff_exec(database,sql,message),SQLITE_OK)
   end subroutine
end program
