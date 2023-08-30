export class CreateAuthDto {}
import { IsEmail, IsString, Length } from 'class-validator';
// eslint-disable-next-line @typescript-eslint/no-namespace
export namespace AuthDTO {
  export class SignUp {
    @IsEmail()
    email: string;

    @IsString()
    @Length(4, 20)
    password: string;

    @IsString()
    nickname: string;
  }

  export class SignIn {
    @IsEmail()
    email: string;

    @IsString()
    @Length(4, 20)
    password: string;
  }
}
