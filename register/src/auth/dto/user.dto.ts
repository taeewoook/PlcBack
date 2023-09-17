export class UserDTO {
  id: number;
  email: string;
  name: string;
  password: string;
}

export class ChangPwd {
  email: string;
  nowpassword: string;
  changepassword: string;
}

export class ChangeEmail {
  nowemail: string;
  changeemail: string;
  password: string;
}