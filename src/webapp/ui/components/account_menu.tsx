import React from "react";
import { HamburgerIcon } from "@chakra-ui/icons";
import {
  Button,
  Menu,
  MenuButton,
  MenuGroup,
  MenuItem,
  MenuList,
} from "@chakra-ui/react";
import { useNavigate } from "react-router-dom";
import { useConfig } from "../../config";
import { useAuth } from "../pages/login/hooks";

type AccountMenuProps = {
  username: string;
};

export const AccountMenu: React.FunctionComponent<AccountMenuProps> = (
  props: AccountMenuProps,
): React.ReactElement => {
  const config = useConfig();
  const auth = useAuth();
  const token = auth.authenticatedUser?.token || "";
  const navigate = useNavigate();
  const onClick = () => {
    auth.forget(async () => {
      await config.uow.account.removeCurrent();
      await config.api.account.logout(token);
      navigate("/admin/login");
    });
  };
  return (
    <Menu>
      <MenuButton as={Button} colorScheme="cyan" rightIcon={<HamburgerIcon />}>
        {props.username}
      </MenuButton>
      <MenuList>
        <MenuGroup title={props.username}>
          <MenuItem onClick={onClick}>Logout</MenuItem>
        </MenuGroup>
      </MenuList>
    </Menu>
  );
};
