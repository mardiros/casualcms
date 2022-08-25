import { EditIcon } from "@chakra-ui/icons";
import {
  Box,
  Icon,
  Table,
  TableContainer,
  Tbody,
  Td,
  Th,
  Thead,
  Tr,
} from "@chakra-ui/react";
import { Result } from "neverthrow";
import React from "react";
import { Link } from "react-router-dom";
import { PartialSite } from "../../casualcms/domain/model";
import { ApiError } from "../../casualcms/domain/ports";
import { AppConfig, AppContext } from "../../config";
import { ApiErrorUI } from "../layout/error_api";
import { Loader } from "../layout/loader";
import { useAuth } from "../login/hooks";

export const SettingList: React.FunctionComponent<{}> = () => {
  const config = React.useContext(AppContext);
  let auth = useAuth();
  const token = auth.authenticatedUser?.token || "";

  return <Box>TODO</Box>;
};
