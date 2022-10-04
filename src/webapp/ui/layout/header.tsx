import { Box, Flex, Heading, Spacer } from "@chakra-ui/react";
import { Link } from "react-router-dom";
import { useAuth } from "../login/hooks";
import { AccountMenu } from "./account_menu";

export const Header: React.FunctionComponent<{}> = (): React.ReactElement => {
  let auth = useAuth();
  return (
    <Flex minWidth="max-content" alignItems="center" gap="2">
      <Box p="2">
        <Heading size="lg" color="cyan.50">
          <Link to="/admin">👕 Casual CMS</Link>
        </Heading>
      </Box>
      <Spacer />
      <Box gap="2">
        {auth.authenticatedUser ? (
          <AccountMenu username={auth.authenticatedUser.username} />
        ) : (
          <Box
            as="button"
            borderRadius="md"
            bg="cyan"
            color="white"
            px={8}
            h={8}
          >
            <Link to="/admin/login" color="white">
              Sign In
            </Link>
          </Box>
        )}
      </Box>
    </Flex>
  );
};
