import React from "react";
import { Box, Flex, Heading, Spacer } from "@chakra-ui/react";
import { Link } from "react-router-dom";
import { useAuth } from "../pages/login/hooks";
import { AccountMenu } from "./account_menu";
import { TShirt64 } from "../images/tshirt64";

export const Header: React.FunctionComponent<{}> = (): React.ReactElement => {
  let auth = useAuth();
  return (
    <Flex minWidth="max-content" alignItems="center" gap="2">
      <Box p="2">
        <Heading size="lg" color="cyan.50">
          <Link to="/admin" style={{ "display": "flex", "alignItems": "flex-end", "columnGap": "1rem" }}>
            <TShirt64 />
            Casual CMS
          </Link>
        </Heading>
      </Box>
      <Spacer />
      <Box gap="2">
        {auth.authenticatedUser ? (
          <AccountMenu username={auth.authenticatedUser.username} />
        ) : (
          <Box as="button" borderRadius="md" bg="cyan" color="white" px={8} h={8}>
            <Link to="/admin/login" color="white">
              Sign In
            </Link>
          </Box>
        )}
      </Box>
    </Flex>
  );
};
