import { Module } from '@nestjs/common';
import { AuthModule } from './auth/auth.module';
import { TypeOrmModule } from '@nestjs/typeorm';
import { User } from './auth/enity/user.entity';
import { TypeOrmExModule } from './db/typeorm-ex.module';
import { UserRepository } from './auth/user.repository';

@Module({
  imports: [
    TypeOrmModule.forRoot({
      type: 'mysql',
      host: 'localhost',
      port: 3306,
      username: 'root',
      password: '1234',
      database: 'practice',
      entities: [User],
      synchronize: true,
    }),
    TypeOrmExModule.forCustomRepository([UserRepository]),
    AuthModule,
  ],
})
export class AppModule {}
