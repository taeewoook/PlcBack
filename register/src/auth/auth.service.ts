import {
  HttpException,
  HttpStatus,
  Injectable,
  UnauthorizedException,
} from '@nestjs/common';
import { UserService } from './user.service';
import { UserDTO, ChangPwd, ChangeEmail } from './dto/user.dto';
import * as bcrypt from 'bcrypt';
import { JwtService } from '@nestjs/jwt';

@Injectable()
export class AuthService {
  constructor(
    private userService: UserService,
    private jwtService: JwtService,
  ) {}
  async changePassword(password: string): Promise<string> {
    return await bcrypt.hash(password, 10);
  }

  async transformPassword(user: UserDTO): Promise<void> {
    user.password = await bcrypt.hash(user.password, 10);
    return Promise.resolve();
  }
  async registerUser(newUser: UserDTO): Promise<UserDTO> {
    let userFind: UserDTO = await this.userService.findByFields({
      where: { email: newUser.email },
    });
    if (userFind) {
      throw new HttpException('user already used!', HttpStatus.BAD_REQUEST);
    }
    await this.transformPassword(newUser);
    return await this.userService.save(newUser);
  }

  async validateUser(
    newUser: UserDTO,
  ): Promise<{ accessToken: string; id: number; name: string } | undefined> {
    let userFind: UserDTO = await this.userService.findByFields({
      where: { email: newUser.email },
    });
    if (!userFind) {
      throw new HttpException('no user', HttpStatus.BAD_REQUEST);
    }
    const validatePassword = await bcrypt.compare(
      newUser.password,
      userFind.password,
    );
    if (!validatePassword) {
      throw new UnauthorizedException();
    }
    const payload = { email: userFind.email, name: userFind.name };

    return {
      accessToken: this.jwtService.sign(payload),
      id: userFind.id,
      name: userFind.name,
    };
  }

  async changePsw(changpwd: ChangPwd): Promise<string> {
    let userFind: UserDTO = await this.userService.findByFields({
      where: { email: changpwd.email },
    });
    if (!userFind) {
      throw new HttpException('no user', HttpStatus.BAD_REQUEST);
    }
    const validatePassword = await bcrypt.compare(
      changpwd.nowpassword,
      userFind.password,
    );
    if (!validatePassword) {
      throw new UnauthorizedException();
    }
    userFind.password = await this.changePassword(changpwd.changepassword);
    await this.userService.save(userFind);
    return 'Success';
  }

  async changeEmail(changeEmail: ChangeEmail): Promise<string> {
    let userFind: UserDTO = await this.userService.findByFields({
      where: { email: changeEmail.nowemail },
    });
    if (!userFind) {
      throw new HttpException('no user', HttpStatus.BAD_REQUEST);
    }
    const validatePassword = await bcrypt.compare(
      changeEmail.password,
      userFind.password,
    );
    if (!validatePassword) {
      throw new UnauthorizedException();
    }
    let user: UserDTO = await this.userService.findByFields({
      where: { email: changeEmail.changeemail },
    });
    if (user) {
      throw new HttpException('user already used!', HttpStatus.BAD_REQUEST);
    }
    userFind.email = changeEmail.changeemail;
    await this.userService.save(userFind);
    return 'Success';
  }

  async deleteUser(newUser: UserDTO): Promise<string> {
    let userFind: UserDTO = await this.userService.findByFields({
      where: { email: newUser.email },
    });
    if (!userFind) {
      throw new HttpException('no user', HttpStatus.BAD_REQUEST);
    }
    const validatePassword = await bcrypt.compare(
      newUser.password,
      userFind.password,
    );
    if (!validatePassword) {
      throw new UnauthorizedException();
    }
    return this.userService.delete(userFind);
  }
}
