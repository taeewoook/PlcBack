import {
  Controller,
  Post,
  Req,
  Body,
  Get,
  Patch,
  Delete,
} from '@nestjs/common';
import { UserDTO, ChangPwd, ChangeEmail } from './dto/user.dto';
import { AuthService } from './auth.service';
import { Request } from '@nestjs/common';

@Controller('auth')
export class AuthController {
  constructor(private authService: AuthService) {}

  @Post('/sign-up')
  async singup(
    @Req() req: Request,
    @Body() UserDTO: UserDTO,
  ): Promise<UserDTO> {
    return await this.authService.registerUser(UserDTO);
  }

  @Post('/login')
  async login(
    @Body() UserDTO: UserDTO,
  ): Promise<{ accessToken: string } | undefined> {
    return await this.authService.validateUser(UserDTO);
  }

  @Patch('/pswchange')
  async pswupdate(
    @Req() req: Request,
    @Body() ChangPwd: ChangPwd,
  ): Promise<string> {
    return await this.authService.changePsw(ChangPwd);
  }

  @Patch('/emailchange')
  async emailupdate(
    @Req() req: Request,
    @Body() ChangeEmail: ChangeEmail,
  ): Promise<string> {
    return await this.authService.changeEmail(ChangeEmail);
  }
  // @Delete('/deleteUser')
  // async del(
  //   @Req() req: Request,
  //   @Body() UserDTO: UserDTO,
  // ): Promise<string | undefined> {
  //   return await this.authService.deleteUser(UserDTO);
  // }
}
