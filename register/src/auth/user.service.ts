import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { UserRepository } from './user.repository';
import { UserDTO } from './dto/user.dto';
import { FindOneOptions } from 'typeorm';

@Injectable()
export class UserService {
  constructor(
    @InjectRepository(UserRepository)
    private userRepository: UserRepository,
  ) {}

  //등록이 된 유저인지 확인
  async findByFields(
    options: FindOneOptions<UserDTO>,
  ): Promise<UserDTO | undefined> {
    return await this.userRepository.findOne(options);
  }

  //신규 유저 등록
  async save(userDTO: UserDTO): Promise<UserDTO | undefined> {
    return await this.userRepository.save(userDTO);
  }

  async delete(userDTO: UserDTO): Promise<string | undefined> {
    // console.log(userDTO);
    await this.userRepository.softDelete({ id: userDTO.id });
    return 'delete complete';
  }
}
