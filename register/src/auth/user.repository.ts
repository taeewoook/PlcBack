import { Injectable } from '@nestjs/common';
import { EntityRepository, Repository } from 'typeorm';
import { User } from './enity/user.entity';
import { CustomRepository } from 'src/db/typeorm-ex.decorator';

@CustomRepository(User)
export class UserRepository extends Repository<User> {}
