import {
  Body,
  ConflictException,
  Controller,
  Get,
  Post,
  Req,
  UseGuards,
  Request,
} from '@nestjs/common';

import { UserService } from './user.service';
import { AuthDTO } from 'src/auth/dto/create-auth.dto';
import { UserEntity } from './entities/user.entity';
import { AuthGuard } from 'src/auth/guard/auth.guard';
console.log(UserEntity);

@Controller('user')
export class UserController {
  constructor(private readonly userService: UserService) {}

  @Post('/signup')
  async signup(@Body() authDTO: AuthDTO.SignUp) {
    const { email, nickname } = authDTO;

    const hasEmail = await this.userService.findByEmail(email);
    if (hasEmail) {
      throw new ConflictException('이미 사용중인 이메일 입니다.');
    }

    const hasNickname = await this.userService.findByNickname(nickname);
    if (hasNickname) {
      throw new ConflictException('이미 사용중인 닉네임 입니다.');
    }

    const userEntity = await this.userService.create(authDTO);
    console.log(userEntity);
    return '회원가입성공';
  }

  @UseGuards(AuthGuard)
  @Get('/')
  async getProfile(@Req() req: any) {
    const user = req.user;
    return user;
  }
}
